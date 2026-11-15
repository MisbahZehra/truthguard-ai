"""Tavily Search API client (POST https://api.tavily.com/search, Bearer auth)."""
import asyncio, random, time
import re
from datetime import date, datetime, timezone
from urllib.parse import urlsplit
import httpx
from ..schemas import Source
from ..intelligence.sources import domain_of, parse_date


MONTH = r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
DATE_IN_PATH = re.compile(r"(?:^|/)(\d{4})[-/](\d{2})[-/](\d{2})(?=/|$)")
DATE_VALUE = rf"(?:\d{{4}}-\d{{2}}-\d{{2}}|(?:{MONTH})\s+\d{{1,2}}(?:st|nd|rd|th)?[,]?\s+\d{{4}}|\d{{1,2}}\s+(?:{MONTH})\s+\d{{4}})"
LABELLED_DATE = re.compile(
    rf"\b(?:last\s+)?(?:updated|published)(?:\s+on)?\s*[:\-]?\s*({DATE_VALUE})",
    re.IGNORECASE,
)


class TavilyError(Exception):
    pass


def _infer_date(url: str, text: str) -> date | None:
    path = urlsplit(url).path
    match = DATE_IN_PATH.search(path)
    if match:
        try:
            return date(*(int(part) for part in match.groups()))
        except ValueError:
            pass
    match = LABELLED_DATE.search(text)
    return parse_date(match.group(1)) if match else None


class TavilyClient:
    URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str, cache_ttl: int = 900, http: httpx.AsyncClient | None = None, retries: int = 3):
        self.key, self.ttl, self.retries = api_key, cache_ttl, retries
        self.http = http or httpx.AsyncClient(timeout=20)
        self._cache: dict[tuple, tuple[float, datetime, list[dict]]] = {}
        self.calls = 0

    async def search(self, query: str, max_results: int = 5, topic: str = "general",
                     time_range: str | None = None, include_domains: list[str] | None = None) -> list[Source]:
        key = (query, max_results, topic, time_range, tuple(include_domains or ()))
        hit = self._cache.get(key)
        if hit and time.time() - hit[0] < self.ttl:
            return self._to_sources(hit[2], hit[1], from_cache=True)  # original retrieval time preserved
        payload = {"query": query, "search_depth": "advanced", "max_results": max_results,
                   "topic": topic, "include_raw_content": False}
        if time_range:
            payload["time_range"] = time_range
        if include_domains:
            payload["include_domains"] = include_domains
        data = await self._post(payload)
        now = datetime.now(timezone.utc)
        self._cache[key] = (time.time(), now, data.get("results", []))
        return self._to_sources(data.get("results", []), now, from_cache=False)

    async def _post(self, payload: dict) -> dict:
        last = None
        for attempt in range(self.retries):
            try:
                self.calls += 1
                r = await self.http.post(self.URL, json=payload, headers={"Authorization": f"Bearer {self.key}"})
                if r.status_code in (401, 403):
                    raise TavilyError(f"Tavily rejected credentials ({r.status_code})")
                if r.status_code == 429:
                    raise TavilyError("Tavily rate limit reached. Try again shortly.")
                if r.status_code >= 500:
                    last = TavilyError("Tavily is temporarily unavailable.")
                else:
                    try:
                        r.raise_for_status()
                    except httpx.HTTPStatusError as e:
                        raise TavilyError(f"Tavily rejected the search request (HTTP {r.status_code}).") from e
                    try:
                        data = r.json()
                    except ValueError as e:
                        raise TavilyError("Tavily returned an invalid response.") from e
                    if not isinstance(data, dict):
                        raise TavilyError("Tavily returned an invalid response.")
                    return data
            except TavilyError:
                raise
            except httpx.TimeoutException:
                last = TavilyError("Timed out connecting to Tavily.")
            except httpx.HTTPError:
                last = TavilyError("Could not connect to Tavily.")
            if attempt + 1 < self.retries:
                await asyncio.sleep(min(8, 0.5 * 2 ** attempt) * (0.5 + random.random()) * (0 if self.retries and getattr(self, "fast", False) else 1))
        raise TavilyError(str(last) if last else "Tavily request failed.")

    @staticmethod
    def _to_sources(results: list[dict], retrieved: datetime, from_cache: bool) -> list[Source]:
        out = []
        for r in results:
            url = r.get("url")
            if not url:
                continue
            content = r.get("content") or ""
            excerpt = content[:1500]
            published_date = parse_date(r.get("published_date"))
            inferred = False
            if published_date is None:
                published_date = _infer_date(url, content)
                inferred = published_date is not None
            out.append(Source(title=r.get("title") or url, url=url, domain=domain_of(url),
                              published_date=published_date, published_date_inferred=inferred,
                              retrieved_at=retrieved, excerpt=excerpt,
                              relevance=float(r.get("score") or 0.5),
                              from_cache=from_cache))
        return out
