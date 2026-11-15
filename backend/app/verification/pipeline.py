import asyncio
from datetime import date, datetime, timezone
from uuid import uuid4
from ..schemas import (ClaimResult, Source, Stance, Status, VerificationResult, VerifyRequest, Claim, Volatility)
from ..integrations.tavily import TavilyError
from ..intelligence.engine import decide
from ..intelligence.freshness import evidence_confidence, source_reliability
from ..intelligence.sources import classify_source, dedupe
from ..security.guards import redact, sanitize_untrusted

LIVE_NOTICE = "Evidence-based verification using available sources at the time of checking. Not a guarantee of truth."
DEMO_NOTICE = "DEMO MODE: all sources are simulated and are NOT live Tavily results. Set TAVILY_API_KEY for live verification."
NEWS_TIME_RANGE = {
    Volatility.VERY_HIGH: "week",
    Volatility.HIGH: "month",
    Volatility.MEDIUM: "year",
    Volatility.LOW: "year",
    Volatility.STABLE: "year",
}


def build_queries(claim: Claim, today: date) -> list[str]:
    base = claim.normalized
    q2 = " ".join(claim.entities[:3] + ["latest official"] + ([str(today.year)] if claim.volatility.value in ("very_high", "high") else []))
    return [base, q2] if q2.strip() != base else [base]


async def _verify_claim(claim, req, search, llm, today, sem):
    if not claim.time_sensitive:
        st, _, why, _, al = decide(claim, [], today)
        return ClaimResult(claim=claim, status=st, explanation=why, alerts=al)
    queries = build_queries(claim, today)
    topic = "news" if claim.category == "News / Current Events" else "general"
    searches = [(query, topic, None) for query in queries]
    searches.append((claim.normalized, "news", NEWS_TIME_RANGE[claim.volatility]))
    try:
        async with sem:
            results = await asyncio.gather(*[
                search.search(query, max_results=req.max_results, topic=search_topic, time_range=time_range)
                for query, search_topic, time_range in searches
            ], return_exceptions=True)
        batches, failures = [], []
        for result in results:
            if isinstance(result, TavilyError):
                failures.append(result)
            elif isinstance(result, BaseException):
                raise result
            else:
                batches.append(result)
        if not batches and failures:
            raise failures[0]
    except TavilyError as e:
        return ClaimResult(claim=claim, status=Status.UNVERIFIABLE, queries=queries,
                           explanation=f"Live verification could not be completed: {e}",
                           alerts=["Search provider unavailable; no data was invented."])
    sources: list[Source] = dedupe([s for b in batches for s in b])
    flagged = False
    alerts = [f"A live search failed: {error}" for error in failures]
    for s in sources:
        s.excerpt, f = sanitize_untrusted(s.excerpt)
        flagged |= f
        s.source_type, s.authority = classify_source(s.url, claim.entities)
    sources = sorted(sources, key=lambda s: -(s.authority * s.relevance))[:6]
    judgement = await llm.judge(claim, [{"url": s.url, "title": s.title, "excerpt": s.excerpt} for s in sources])
    for s in sources:
        s.stance = judgement.stances.get(s.url, Stance.NEUTRAL)
    st, fresh, why, conflict, decision_alerts = decide(claim, sources, today)
    alerts.extend(decision_alerts)
    if flagged:
        alerts.append("A retrieved source contained instruction-like text; it was neutralized and treated as data.")
    return ClaimResult(claim=claim, status=st, freshness_score=fresh, evidence_confidence=evidence_confidence(sources),
                       source_reliability=source_reliability(sources), explanation=why, sources=sources, conflict=conflict,
                       suggested_correction=judgement.correction if st in (Status.STALE, Status.CONTRADICTED, Status.POTENTIALLY_OUTDATED) else None,
                       alerts=alerts, queries=queries)


def summarize(results: list[ClaimResult]) -> dict:
    counts: dict[str, int] = {}
    for r in results:
        counts[r.status.value] = counts.get(r.status.value, 0) + 1
    checked = [r for r in results if r.status != Status.NOT_TIME_SENSITIVE]
    covered = [r for r in checked if any(s.stance != Stance.NEUTRAL for s in r.sources)]
    return {"total_claims": len(results), "counts": counts,
            "evidence_coverage": round(len(covered) / len(checked), 2) if checked else None,
            "needs_attention": sum(counts.get(k, 0) for k in ("STALE", "CONTRADICTED", "POTENTIALLY_OUTDATED"))}


def build_verified_answer(answer: str, results: list[ClaimResult], as_of: date):
    text, changes, cites = answer, [], {}
    def cite(r):
        used = [s for s in r.sources if s.stance != Stance.NEUTRAL][:1]
        for s in used:
            cites.setdefault(s.url, (len(cites) + 1, s))
        return "".join(f"[{cites[s.url][0]}]" for s in used)
    for r in results:
        orig = r.claim.original_text
        if orig not in text:
            continue
        c = cite(r)
        if r.status in (Status.STALE, Status.CONTRADICTED) and r.suggested_correction:
            new = f"{r.suggested_correction.rstrip('.')}. {c}".strip()
            kind = "updated"
        elif r.status in (Status.STALE, Status.CONTRADICTED):
            new, kind = f"{orig} (disputed by newer evidence {c})", "qualified"
        elif r.status == Status.POTENTIALLY_OUTDATED:
            new, kind = f"{orig} (may be outdated {c})", "qualified"
        elif r.status == Status.VERIFIED_CURRENT:
            new, kind = f"{orig} {c}", "cited"
        elif r.status == Status.NOT_TIME_SENSITIVE:
            continue
        else:
            new, kind = f"{orig} (unverified)", "qualified"
        text = text.replace(orig, new, 1)
        changes.append({"claim_id": r.claim.id, "type": kind, "before": orig, "after": new})
    refs = "\n".join(f"[{n}] {s.title} — {s.url}" + (f" (published {s.published_date})" if s.published_date else " (publication date unknown)")
                     for n, s in sorted(cites.values(), key=lambda x: x[0]))
    return f"As of {as_of}:\n{text}" + (f"\n\nSources:\n{refs}" if refs else ""), changes


async def verify(req: VerifyRequest, *, live: bool, search, llm, concurrency: int = 4) -> VerificationResult:
    today = req.as_of or date.today()
    answer = redact(req.answer)
    warnings = ["Sensitive-looking tokens were redacted before processing."] if answer != req.answer else []
    claims = await llm.extract_claims(answer, req.max_claims)
    sem = asyncio.Semaphore(concurrency)
    results = await asyncio.gather(*[_verify_claim(c, req, search, llm, today, sem) for c in claims])
    verified, changes = build_verified_answer(answer, list(results), today)
    if not claims:
        warnings.append("No verifiable factual claims were found.")
    return VerificationResult(id=uuid4().hex[:12], created_at=datetime.now(timezone.utc), mode="live" if live else "demo",
                              notice=LIVE_NOTICE if live else DEMO_NOTICE, answer=answer, as_of=today,
                              claims=list(results), summary=summarize(list(results)),
                              verified_answer=verified, changes=changes, warnings=warnings)
