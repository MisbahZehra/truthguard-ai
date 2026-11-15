# TruthGuard AI — The Intelligence Layer That Keeps AI Answers Fresh.

Demo video: https://youtu.be/pvox7-3eSfk 
Claim-level stale-answer detection: extracts factual claims from an LLM answer, researches each via Tavily
(`POST https://api.tavily.com/search`), scores freshness per claim, and rebuilds a cited, corrected answer.
Evidence-based verification using available sources at the time of checking — not a guarantee of truth.

## Install and run
```bash
cp .env.example .env
cd backend && pip install -r requirements.txt && python -m pytest -q
cd ../frontend && npm install && npm test && npm run build
cd ../backend && STATIC_DIR=../frontend/dist uvicorn app.main:create_app --factory --port 8000
```
Open http://localhost:8000 (web app) or http://localhost:8000/docs (OpenAPI). Docker: `docker compose up --build`.

## Run on Windows
Install Python 3.12 and Node.js, then create the root environment file and add your own provider credentials:
```powershell
Copy-Item .env.example .env
# Edit .env without committing it; see Environment variables below.
.\start.ps1
```
`start.ps1` starts the API and built UI on port 8000. It builds the frontend if `frontend\dist` is missing.
After configuring the environment, verify two live claims with:
```powershell
.\test_live.ps1
```
`test_live.ps1` refuses to submit requests while the server is in demo mode.

## Environment variables
Set values in the repository-root `.env` file; never commit that file. `.env.example` contains empty credential fields.

| Variable | Purpose |
| --- | --- |
| `TAVILY_API_KEY` | Enables live Tavily search; empty means clearly labelled demo mode. |
| `LLM_BASE_URL` | OpenAI-compatible provider endpoint; for Groq use `https://api.groq.com/openai/v1`. |
| `LLM_API_KEY` | Provider key for LLM-assisted claim extraction and evidence judging. |
| `LLM_MODEL` | Model name accepted by the configured provider, for example `openai/gpt-oss-120b`. |
| `TRUTHGUARD_API_KEYS` | Comma-separated API keys required by protected API routes. |
| `DB_PATH` | SQLite database path. |
| `CACHE_TTL_SECONDS` | Search cache lifetime in seconds. |
| `RATE_LIMIT_PER_MIN` | Per-process request limit per minute. |
| `UI_ENABLED` | Enables or disables the web UI routes. |
| `RETENTION_DAYS` | Age threshold for persisted verification history cleanup. |

Tavily is the live search provider. Leave `LLM_API_KEY` empty to use the deterministic heuristic judge, or configure an OpenAI-compatible provider such as Groq with its base URL, key, and supported model.

## Features
Claim extraction & classification · Tavily research with cache/retry · per-claim freshness, confidence, reliability ·
conflict detection · cited corrected answer with diff · history with filters · Markdown report export · batch API ·
API-key auth, rate limits, request IDs · retention policy · demo mode (simulated, always labelled).

## How Tavily search is used
Each claim receives general web search; time-sensitive claims also receive one bounded news search to look for dated reporting.
The news time range depends on claim volatility. Results are deduplicated and cached. Tavily-reported dates can establish freshness;
conservatively recovered URL/text dates are labelled inferred and do not establish freshness. Missing dates remain unknown.

## Screenshots
Project screenshots can be added to [docs/screenshots/](docs/screenshots/).

## Docs
docs/ARCHITECTURE.md · API.md · VERIFICATION_ENGINE.md · FRESHNESS_METHODOLOGY.md · SECURITY.md · INSTALLATION.md · DEMO_GUIDE.md · SUBMISSION.md

## Limitations
Automated provider tests use mocked HTTP; live results depend on provider availability and source quality. The built-in
heuristic judge compares numbers/versions only; configure an LLM for semantic judgement. SQLite only; synchronous
verification; in-memory rate limiter/cache (single process). URL/document ingestion, PostgreSQL, PDF export and runtime
settings editing are not implemented. Docker files are untested.

## Roadmap
URL/document ingestion with the SSRF guard, PostgreSQL, async jobs, editable policies, PDF reports.
