"""Transparent scoring. See docs/FRESHNESS_METHODOLOGY.md."""
from datetime import date
from ..schemas import Volatility, Source, Stance

# Half-life (days): after this age, evidence recency contributes 50.
HALF_LIFE = {Volatility.VERY_HIGH: 1, Volatility.HIGH: 30, Volatility.MEDIUM: 180,
             Volatility.LOW: 1095, Volatility.STABLE: 36500}

CATEGORY_VOLATILITY = [
    ("Pricing / Financial", ["stock", "share price", "market cap", "exchange rate"], Volatility.VERY_HIGH),
    ("Pricing / Financial", ["$", "price", "pricing", "per month", "subscription", "costs"], Volatility.HIGH),
    ("Software / API / Technology", ["version", "release", "api", "sdk", "python", "node", "v1", "v2"], Volatility.HIGH),
    ("Company / Leadership", ["ceo", "cto", "chairman", "led by", "president", "founder", "employees"], Volatility.MEDIUM),
    ("Legal / Regulatory", ["law", "regulation", "act ", "legal", "gdpr", "tax rate"], Volatility.MEDIUM),
    ("News / Current Events", ["announced", "recently", "this week", "today"], Volatility.VERY_HIGH),
    ("Statistics / Research", ["percent", "%", "population", "study", "survey"], Volatility.MEDIUM),
    ("Geography / Public Information", ["capital of", "located in", "border"], Volatility.STABLE),
]


def classify(text: str) -> tuple[str, Volatility]:
    t = text.lower()
    if any(k in t for k in ["boils at", "square root", "theorem", "world war", "was founded in", "invented", "pi is"]):
        return "Other", Volatility.STABLE
    for cat, kws, vol in CATEGORY_VOLATILITY:
        if any(k in t for k in kws):
            return cat, vol
    return "Other", Volatility.MEDIUM


def recency_score(published: date | None, today: date, volatility: Volatility) -> int | None:
    """None when the publication date is unknown: we do not invent a number."""
    if published is None:
        return None
    age = max((today - published).days, 0)
    return round(100 * 0.5 ** (age / HALF_LIFE[volatility]))


def evidence_confidence(sources: list[Source]) -> float:
    """Agreement x authority x relevance x coverage, in [0,1]. Not a probability of truth."""
    used = [s for s in sources if s.stance != Stance.NEUTRAL]
    if not used:
        return 0.0
    w = lambda s: s.authority * s.relevance
    sup = sum(w(s) for s in used if s.stance == Stance.SUPPORTS)
    con = sum(w(s) for s in used if s.stance == Stance.CONTRADICTS)
    agreement = max(sup, con) / (sup + con)
    strength = sum(w(s) for s in used) / len(used)
    domains = len({s.domain for s in used})
    coverage = min(1.0, 0.5 + 0.25 * domains)
    return round(agreement * strength * coverage, 2)


def source_reliability(sources: list[Source]) -> float:
    used = [s for s in sources if s.stance != Stance.NEUTRAL] or sources
    return round(sum(s.authority for s in used) / len(used), 2) if used else 0.0
