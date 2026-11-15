from .schemas import VerificationResult, Stance


def to_markdown(r: VerificationResult) -> str:
    L = [f"# TruthGuard Verification Report `{r.id}`", "", f"- Verified at: {r.created_at.isoformat()}",
         f"- Mode: **{r.mode.upper()}**", f"- As-of date: {r.as_of}", f"- Note: {r.notice}", "",
         "## Submitted answer", "", r.answer, "", "## Summary", ""]
    L += [f"- {k}: {v}" for k, v in r.summary["counts"].items()]
    L += ["", "## Claims", ""]
    for c in r.claims:
        L += [f"### {c.claim.id}: {c.claim.normalized}", f"- Status: **{c.status.value}**",
              f"- Freshness: {c.freshness_score if c.freshness_score is not None else 'not established (no reliable dates)'}",
              f"- Evidence confidence: {c.evidence_confidence} | Source reliability: {c.source_reliability}",
              f"- Volatility: {c.claim.volatility.value} | Category: {c.claim.category}", f"- Why: {c.explanation}"]
        if c.suggested_correction:
            L.append(f"- Suggested correction: {c.suggested_correction}")
        for s in c.sources:
            tag = " (SIMULATED)" if s.simulated else ""
            inferred = " (inferred)" if s.published_date_inferred else ""
            L.append(f"  - [{s.stance.value}] {s.title}{tag} — {s.url} — published {s.published_date or 'unknown'}{inferred}, "
                     f"retrieved {s.retrieved_at.isoformat()}{' (cached)' if s.from_cache else ''}")
        L.append("")
    L += ["## Verified answer", "", r.verified_answer or "", ""]
    return "\n".join(L)
