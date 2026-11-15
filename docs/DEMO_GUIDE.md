# Demo guide and 3-minute judge script
Without keys the app is in labelled DEMO MODE (fictional "Acme Cloud", simulated sources). With `TAVILY_API_KEY` it uses real Tavily results; never present demo output as live.
**0:00** Landing page: "AI answers sound confident even when facts changed. We score every claim separately."
**0:30** Workspace -> "Full demo answer" -> Verify. Point at the banner and the per-claim cards.
**1:00** Python claim: STALE; open evidence (source, date, excerpt). Pricing claim: STALE with cited correction.
**1:45** Employees claim: sources disagree -> INSUFFICIENT_EVIDENCE, we refuse to force a verdict. Water boils: not time-sensitive, no search spent.
**2:15** Original vs verified diff, copy, export report. **2:40** Developer center: one POST call integrates it into any LLM app.
**3:00** For a live run: set a Tavily key, paste a real answer with a version and a price, repeat.
Strong points: claim-level metrics kept separate, no invented freshness when dates are missing, conflict handling, validated corrections, honest demo labelling.
