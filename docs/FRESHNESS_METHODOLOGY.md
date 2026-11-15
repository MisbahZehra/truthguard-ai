# Freshness Methodology

Four separate values per claim (never merged):
- **Verification status** – rule-based decision from evidence stances (`intelligence/engine.py`).
- **Freshness score (0–100)** – `100 · 0.5^(age_days / half_life)` of the newest source with a reported publication date.
  Half-lives: very_high 1d, high 30d, medium 180d, low 3y, stable ~100y. `null` when no reported date exists.
- **Evidence confidence (0–1)** – agreement × mean(authority·relevance) × domain coverage. Not a probability of truth.
- **Source reliability (0–1)** – mean authority: government 1.0, official docs 0.92, official company 0.9,
  research 0.85, news 0.7, secondary 0.5, other 0.4. Popularity is not used.

Decision rules: contradiction by dated source with authority ≥0.8 → STALE; <0.6 → POTENTIALLY_OUTDATED; otherwise
CONTRADICTED. Only reported dates can establish freshness or make a contradiction STALE; inferred dates never
contribute to the score. Dates recovered from a full date in the URL path or an explicitly labelled Updated/Published
date in source text are shown as inferred, with an alert, and are not treated as provider-reported dates.

Time-sensitive claims receive the existing general search(es) plus one bounded news search. The news search uses a
week for very-high volatility, a month for high volatility, and a year for medium or lower volatility. Results are
deduplicated by URL while preferring a reported date over an inferred date; separate general/news cache keys preserve
the existing cache behavior.

Support and contradiction of similar authority (<0.25 apart) → INSUFFICIENT_EVIDENCE (conflict shown). For an
undated or inferred-date-only support result, VERIFIED_CURRENT is allowed only if at least two distinct source domains
support the claim or one supporting source has authority ≥0.9, and no source contradicts it. The status includes an
explicit alert and freshness remains “not established.” Otherwise the result remains INSUFFICIENT_EVIDENCE. With
reported dates, support is VERIFIED_CURRENT if freshness ≥40 and POTENTIALLY_OUTDATED if older.
Thresholds and half-lives are heuristics, not guarantees.
