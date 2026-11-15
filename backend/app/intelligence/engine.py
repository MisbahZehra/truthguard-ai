"""Evidence -> status decision. Deterministic and unit-testable."""
from datetime import date
from ..schemas import Claim, Source, Stance, Status
from .freshness import recency_score

FRESH_THRESHOLD = 40


def _reported_date(source: Source):
    return source.published_date if source.published_date and not source.published_date_inferred else None


def decide(claim: Claim, sources: list[Source], today: date):
    """Returns (status, freshness, explanation, conflict, alerts)."""
    alerts: list[str] = []
    if any(s.published_date_inferred for s in sources):
        alerts.append("Inferred source dates are displayed but are not used to calculate freshness.")
    if not claim.time_sensitive and not any(s.stance == Stance.CONTRADICTS for s in sources):
        return (Status.NOT_TIME_SENSITIVE, None,
                "Stable fact: freshness checks are not required unless contradicting evidence appears.", False, alerts)
    if not sources:
        return (Status.UNVERIFIABLE, None, "No sources were retrieved for this claim.", False, alerts)
    sup = [s for s in sources if s.stance == Stance.SUPPORTS]
    con = [s for s in sources if s.stance == Stance.CONTRADICTS]
    has_contradiction = bool(con)
    if not sup and not con:
        return (Status.UNVERIFIABLE, None,
                "Sources were retrieved but none addressed the claim directly.", False, alerts)

    if sup and con:
        bs, bc = max(s.authority for s in sup), max(s.authority for s in con)
        if abs(bs - bc) < 0.25:
            alerts.append("Conflicting evidence from sources of comparable authority.")
            dated = [d for s in sup + con if (d := _reported_date(s)) is not None]
            fresh = recency_score(max(dated), today, claim.volatility) if dated else None
            return (Status.INSUFFICIENT_EVIDENCE, fresh,
                    f"Sources disagree: {len(sup)} support and {len(con)} contradict the claim, with comparable "
                    "authority. No conclusion is forced.", True, alerts)
        if bc > bs:
            sup = []
        else:
            con = []

    if con:
        best = max(con, key=lambda s: s.authority)
        published_date = _reported_date(best)
        fresh = recency_score(published_date, today, claim.volatility)
        if not published_date:
            alerts.append("Missing publication date on contradicting source.")
        if best.authority >= 0.8 and published_date:
            st, why = Status.STALE, (f"Newer authoritative evidence ({best.domain}, published "
                                     f"{published_date}) conflicts with the claim.")
        elif best.authority < 0.6 and published_date:
            st, why = Status.POTENTIALLY_OUTDATED, (f"A less authoritative source ({best.domain}, "
                                                    f"{published_date}) suggests different information.")
        else:
            st, why = Status.CONTRADICTED, f"Evidence from {best.domain} conflicts with the claim."
        alerts.append(f"{claim.category}: information appears to have changed.")
        return st, fresh, why, False, alerts

    dated = [(s, published) for s in sup if (published := _reported_date(s)) is not None]
    if not dated:
        if has_contradiction:
            alerts.append("Contradicting sources remain; undated support cannot establish a current fact.")
            return (Status.INSUFFICIENT_EVIDENCE, None,
                    "Supporting and contradicting sources disagree, and no reported publication date resolves the conflict.",
                    True, alerts)
        independent_domains = {s.domain for s in sup}
        authoritative_support = any(s.authority >= 0.9 for s in sup)
        if authoritative_support or len(independent_domains) >= 2:
            alerts.append("Freshness is not established because no reported publication date is available.")
            return (Status.VERIFIED_CURRENT, None,
                    "Supported by authoritative or independent sources with no contradicting evidence; freshness is not established.",
                    False, alerts)
        alerts.append("Missing or unreliable publication dates.")
        return (Status.INSUFFICIENT_EVIDENCE, None,
                "Unable to establish freshness or sufficient independent support because no reported publication date is available.",
                False, alerts)
    newest, newest_date = max(dated, key=lambda item: item[1])
    fresh = recency_score(newest_date, today, claim.volatility)
    if fresh is not None and fresh >= FRESH_THRESHOLD:
        return (Status.VERIFIED_CURRENT, fresh,
                f"Supported by {newest.domain} (published {newest_date}); no contradicting evidence found.",
                False, alerts)
    alerts.append("Supporting evidence is old relative to how quickly this information changes.")
    return (Status.POTENTIALLY_OUTDATED, fresh,
            f"Supported only by older evidence ({newest_date}) for {claim.volatility.value}-volatility information.",
            False, alerts)
