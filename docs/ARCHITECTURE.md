# Architecture
```mermaid
flowchart LR
  B[Browser React UI] -->|/ui/* same-origin, per-IP limit| API
  D[Developer LLM app] -->|/api/v1/* X-API-Key| API
  subgraph API[FastAPI]
    P[Pipeline] --> X[Claim extraction - LLM provider]
    P --> T[Tavily client: retry, cache]
    P --> E[Evidence engine + freshness scoring]
    P --> R[Answer reconstruction]
  end
  T -->|HTTPS Bearer| TV[(Tavily Search API)]
  X -.-> L[(OpenAI-compatible LLM or built-in heuristic)]
  P --> S[(SQLite)]
```
Flow per claim: extract -> classify volatility -> up to 2 targeted queries -> dedupe + authority tagging -> sanitize
excerpts -> judge stances from retrieved evidence only -> deterministic status decision -> correction validated against
excerpts -> cited rewrite. Two route sets share one handler: `/api/v1` (API key) and `/ui` (same-origin, no secret in browser).
Deliberate choices: SQLite via parameterized queries (PostgreSQL is not implemented); synchronous verification (no job queue);
in-memory rate limiter and cache (single process).
