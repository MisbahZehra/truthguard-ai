const curl = `curl -X POST http://localhost:8000/api/v1/verify \\
  -H "X-API-Key: $TRUTHGUARD_API_KEY" -H "Content-Type: application/json" \\
  -d '{"answer": "The latest stable release of Python is 3.9."}'`;
const py = `import httpx
r = httpx.post("http://localhost:8000/api/v1/verify",
               headers={"X-API-Key": KEY}, json={"answer": llm_answer}, timeout=60)
result = r.json()
stale = [c for c in result["claims"] if c["status"] in ("STALE", "CONTRADICTED")]
safe_text = result["verified_answer"]`;
const resp = `{ "id": "a1b2c3d4e5f6", "mode": "live", "claims": [{
    "claim": {"id": "c1", "normalized": "...", "volatility": "high"},
    "status": "STALE", "freshness_score": 63, "evidence_confidence": 0.58,
    "sources": [{"url": "...", "published_date": "2026-10-23", "stance": "contradicts"}] }],
  "verified_answer": "As of 2026-11-12: ...", "changes": [...] }`;
const endpoints = [["POST", "/api/v1/verify", "Verify one answer (synchronous)."], ["POST", "/api/v1/verify/batch", "Up to 10 answers, processed independently."],
  ["GET", "/api/v1/verify/{id}", "Fetch a stored result."], ["GET", "/api/v1/verify/{id}/report", "Markdown report."],
  ["GET", "/api/v1/claims/{id}:{claim_id}", "Claim-level evidence."], ["GET", "/api/v1/history", "Past sessions (q, status, since)."], ["GET", "/api/v1/health", "Health and mode (no auth)."]];
const errors = [["401 unauthorized", "Missing or invalid X-API-Key."], ["404 not_found", "Unknown verification or claim."], ["422 validation_error", "Answer shorter than 10 or longer than 8000 characters, or bad fields."],
  ["429 rate_limited", "Too many requests; see the Retry-After header."], ["500 internal_error", "Unexpected error; quote the request_id."]];
const Code = ({ children }: { children: string }) => <pre className="card p-4 text-xs overflow-x-auto"><code>{children}</code></pre>;

export default function Developer() {
  return (
    <div className="space-y-8 max-w-4xl">
      <h1 className="text-2xl font-semibold text-white">Developer center</h1>
      <section><h2 className="text-white font-medium mb-2">Authentication</h2>
        <p className="text-sm text-slate-300">Send a key from the server's <code>TRUTHGUARD_API_KEYS</code> setting in the <code>X-API-Key</code> header. Keys are never sent to the browser; this web UI uses a separate same-origin route. Interactive OpenAPI docs: <a className="text-accent underline" href="/docs">/docs</a>. Default rate limit: 30 requests/minute per key (configurable). Every response carries <code>X-Request-ID</code>.</p></section>
      <section><h2 className="text-white font-medium mb-2">Endpoints</h2>
        <div className="card divide-y divide-ink-600/60">{endpoints.map(([m, p, d]) => <div key={p} className="p-3 text-sm flex flex-wrap gap-3"><b className="w-12 text-accent">{m}</b><code>{p}</code><span className="text-slate-400">{d}</span></div>)}</div></section>
      <section><h2 className="text-white font-medium mb-2">Example request</h2><Code>{curl}</Code></section>
      <section><h2 className="text-white font-medium mb-2">Integrating with an LLM pipeline</h2><Code>{py}</Code></section>
      <section><h2 className="text-white font-medium mb-2">Example response (abridged)</h2><Code>{resp}</Code></section>
      <section><h2 className="text-white font-medium mb-2">Errors</h2><p className="text-xs text-slate-400 mb-2">Shape: {`{"error": {"code", "message", "request_id"}}`}</p>
        <div className="card divide-y divide-ink-600/60">{errors.map(([c, d]) => <div key={c} className="p-3 text-sm flex gap-3"><code className="w-44 shrink-0">{c}</code><span className="text-slate-400">{d}</span></div>)}</div></section>
    </div>
  );
}
