import re
from urllib.parse import urlparse
from datetime import date, datetime
from ..schemas import Source

NEWS = {"reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nytimes.com", "wsj.com", "ft.com", "bloomberg.com"}
DOC_HINTS = ("docs.", "developer.", "developers.", "/docs", "/release", "/pricing", "/changelog")
RESEARCH = ("arxiv.org", "nature.com", "science.org", "nih.gov", "who.int")


def domain_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def classify_source(url: str, entities: list[str]) -> tuple[str, float]:
    d = domain_of(url)
    if re.search(r"\.(gov|mil|int)(\.[a-z]{2})?$", d) or d.endswith(".gov"):
        return "government", 1.0
    if any(d.endswith(r) for r in RESEARCH) or d.endswith(".edu"):
        return "research", 0.85
    ent = [re.sub(r"[^a-z0-9]", "", e.lower()) for e in entities if len(e) > 2]
    label = re.sub(r"[^a-z0-9]", "", d.split(".")[-2] if d.count(".") and d.split(".")[-2] not in ("co", "com") else d.split(".")[0])
    official = any(e and (e in re.sub(r"[^a-z0-9.]", "", d) or (len(label) > 3 and label in e)) for e in ent)
    if official and any(h in url.lower() or d.startswith(h) for h in DOC_HINTS):
        return "official_docs", 0.92
    if official:
        return "official_company", 0.9
    if any(d == n or d.endswith("." + n) for n in NEWS):
        return "news", 0.7
    if "wikipedia.org" in d:
        return "secondary", 0.5
    return "other", 0.4


def parse_date(v) -> date | None:
    """Parse unambiguous ISO, named-month, or RFC-2822 dates; never guess."""
    if not v:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", str(v))
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            return None
    value = re.sub(r"(?<=\d)(?:st|nd|rd|th)\b", "", str(v).strip(), flags=re.I)
    for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y",
                "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(str(v)).date()
    except (TypeError, ValueError):
        return None


def dedupe(sources: list[Source]) -> list[Source]:
    seen: dict[tuple[str, str], Source] = {}
    out = []
    for s in sorted(sources, key=lambda x: -x.relevance):
        key = (s.domain, re.sub(r"[?#].*$", "", s.url).rstrip("/").lower())
        existing = seen.get(key)
        if existing is None:
            seen[key] = s
            out.append(s)
            continue
        if s.published_date and (
            existing.published_date is None
            or (existing.published_date_inferred and not s.published_date_inferred)
            or (existing.published_date_inferred == s.published_date_inferred
                and s.published_date > existing.published_date)
        ):
            existing.published_date = s.published_date
            existing.published_date_inferred = s.published_date_inferred
    return out
