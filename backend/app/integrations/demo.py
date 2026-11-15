"""Deterministic DEMO search. Every source is SIMULATED (fictional entities) and flagged simulated=True."""
from datetime import datetime, timedelta, timezone
from ..schemas import Source
from ..intelligence.sources import domain_of

DEMO_ANSWER = ("The latest stable release of Python is 3.9. Acme Cloud Pro costs $20 per month. "
               "Acme Cloud has 10,000 employees. Water boils at 100 degrees Celsius at sea level.")


def _src(title, url, days, text, rel=0.9):
    now = datetime.now(timezone.utc)
    pub = (now - timedelta(days=days)).date() if days is not None else None
    return Source(title=f"[SIMULATED] {title}", url=url, domain=domain_of(url), published_date=pub,
                  retrieved_at=now, excerpt=text, relevance=rel, simulated=True)


class DemoSearch:
    calls = 0

    async def search(self, query: str, max_results: int = 5, **_) -> list[Source]:
        self.calls += 1
        q = query.lower()
        if "python" in q:
            return [_src("Python release notes (simulated)", "https://docs.python.org/release", 20,
                         "Python 3.14 is the latest stable release.")]
        if "acme cloud pro" in q or "per month" in q:
            return [_src("Acme Cloud pricing (simulated)", "https://acmecloud.example/pricing", 5,
                         "Acme Cloud Pro now costs $29 per month.")]
        if "employees" in q:
            return [_src("Acme Cloud about page (simulated)", "https://acmecloud.example/about", 30,
                         "Acme Cloud has 12,400 employees worldwide."),
                    _src("Industry digest (simulated)", "https://www.reuters.com/demo-acme", 60,
                         "Acme Cloud, with 10,000 employees, expanded again.", 0.7)]
        return []
