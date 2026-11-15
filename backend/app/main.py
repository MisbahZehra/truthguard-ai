import logging, os, time, uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .config import Settings
from .integrations.demo import DEMO_ANSWER, DemoSearch
from .integrations.llm import HeuristicLLM, LLMError, OpenAICompatLLM
from .integrations.tavily import TavilyClient
from .report import to_markdown
from .schemas import VerifyRequest, VerificationResult
from .store import Store
from .verification.pipeline import verify

logger = logging.getLogger(__name__)


class BatchRequest(BaseModel):
    items: list[VerifyRequest] = Field(min_length=1, max_length=10)


def create_app(settings: Settings | None = None, search=None, llm=None) -> FastAPI:
    s = settings or Settings()
    app = FastAPI(title="TruthGuard AI", version="1.0.0",
                  description="Claim-level freshness verification for LLM answers, powered by Tavily live research.")
    live = (search is not None and not isinstance(search, DemoSearch)) or (search is None and s.live)
    search = search or (TavilyClient(s.tavily_api_key, s.cache_ttl) if s.live else DemoSearch())
    llm_configured = bool(s.llm_base_url and s.llm_api_key and s.llm_model)
    llm_name = "openai-compatible" if llm_configured else "heuristic (built-in, deterministic)"
    llm = llm or (OpenAICompatLLM(s.llm_base_url, s.llm_api_key, s.llm_model) if llm_configured else HeuristicLLM())
    store, hits = Store(s.db_path), defaultdict(deque)
    if s.retention_days > 0:  # retention policy enforced at startup
        store.purge((datetime.now(timezone.utc) - timedelta(days=s.retention_days)).isoformat())

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.rid = rid
        resp = await call_next(request)
        resp.headers["X-Request-ID"] = rid
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        return resp

    def err(request, status, code, msg, headers=None):
        return JSONResponse({"error": {"code": code, "message": msg, "request_id": getattr(request.state, "rid", None)}},
                            status_code=status, headers=headers)

    @app.exception_handler(HTTPException)
    async def http_exc(request, e):
        d = e.detail
        return err(request, e.status_code, d["code"] if isinstance(d, dict) else "http_error",
                   d["message"] if isinstance(d, dict) else str(d), getattr(e, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def val_exc(request, e):
        return err(request, 422, "validation_error", "; ".join(f"{'.'.join(map(str, x['loc'][1:]))}: {x['msg']}" for x in e.errors()))

    @app.exception_handler(LLMError)
    async def llm_exc(request, e):
        exception_type = type(e.__cause__).__name__ if e.__cause__ else type(e).__name__
        logger.error("LLM provider failure type=%s request_id=%s", exception_type, request.state.rid)
        return err(request, 502, "provider_error", str(e))

    @app.exception_handler(Exception)
    async def any_exc(request, e):
        logger.error("Unhandled server error type=%s request_id=%s", type(e).__name__, request.state.rid)
        return err(request, 500, "internal_error", "Unexpected server error.")

    def limit(bucket: str):
        q, now = hits[bucket], time.time()
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= s.rate_limit:
            e = HTTPException(429, {"code": "rate_limited", "message": f"Limit is {s.rate_limit} requests/minute."})
            e.headers = {"Retry-After": str(max(1, int(60 - (now - q[0]))))}
            raise e
        q.append(now)

    async def auth(x_api_key: str | None = Header(default=None)):
        if x_api_key not in s.api_keys:
            raise HTTPException(401, {"code": "unauthorized", "message": "Missing or invalid X-API-Key."})
        limit("k:" + x_api_key)

    async def ui_guard(request: Request):
        """Same-origin browser access. No secret ever reaches the browser; limited per client IP."""
        if not s.ui_enabled:
            raise HTTPException(404, {"code": "not_found", "message": "UI API disabled."})
        limit("ip:" + (request.client.host if request.client else "?"))

    def mode():
        return "live" if live else "demo"

    async def do_verify(req):
        r = await verify(req, live=live, search=search, llm=llm, concurrency=s.concurrency)
        store.save(r)
        return r

    def fetch(vid):
        r = store.get(vid)
        if not r:
            raise HTTPException(404, {"code": "not_found", "message": "Verification not found."})
        return r

    def routes(prefix_guard):
        rt = APIRouter(dependencies=[Depends(prefix_guard)])

        @rt.post("/verify", response_model=VerificationResult)
        async def v(req: VerifyRequest):
            return await do_verify(req)

        @rt.post("/verify/batch", response_model=list[VerificationResult])
        async def b(req: BatchRequest):
            return [await do_verify(i) for i in req.items]  # each answer processed independently

        @rt.get("/verify/{vid}", response_model=VerificationResult)
        async def g(vid: str):
            return fetch(vid)

        @rt.get("/verify/{vid}/report", response_class=PlainTextResponse)
        async def rep(vid: str):
            return PlainTextResponse(to_markdown(fetch(vid)), media_type="text/markdown")

        @rt.get("/claims/{claim_ref}")
        async def c(claim_ref: str):
            vid, _, cid = claim_ref.partition(":")
            r = store.get(vid)
            hit = next((x for x in r.claims if x.claim.id == cid), None) if r else None
            if not hit:
                raise HTTPException(404, {"code": "not_found", "message": "Use '{verification_id}:{claim_id}'."})
            return hit

        @rt.get("/history")
        async def h(q: str | None = None, status: str | None = None, since: str | None = None):
            return {"items": store.history(q, status, since)}
        return rt

    @app.get("/api/v1/health")
    async def health():
        return {"status": "ok", "mode": mode(), "version": app.version}

    app.include_router(routes(auth), prefix="/api/v1")
    app.include_router(routes(ui_guard), prefix="/ui", include_in_schema=False)

    @app.get("/ui/config", include_in_schema=False, dependencies=[Depends(ui_guard)])
    async def cfg():
        return {"mode": mode(), "llm": llm_name, "cache_ttl_seconds": s.cache_ttl, "rate_limit_per_min": s.rate_limit,
                "retention_days": s.retention_days, "concurrency": s.concurrency, "demo_answer": DEMO_ANSWER,
                "tavily_configured": s.live, "version": app.version}

    if s.static_dir and os.path.isdir(s.static_dir):
        app.mount("/", StaticFiles(directory=s.static_dir, html=True), name="web")
    return app
