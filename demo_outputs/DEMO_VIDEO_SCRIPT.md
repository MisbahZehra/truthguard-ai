# TruthGuard AI Demo Video Script

**Recording status:** Preparation scaffold only. No live A/B/C responses have been captured because this checkout has no root `.env` and no API credentials are available in the process environment. Do not describe any result as live until fresh responses and Markdown reports are saved beside this file. Replace bracketed prompts below with values read from those responses; do not infer missing dates, conflicts, or corrections.

## Timed narration (3 minutes)

### 0:00-0:20 | What TruthGuard does
**Paste:** Nothing.
**Point at:** The Workspace, then the live-mode indicator in the app header.
**Say:** “TruthGuard checks factual claims inside an AI-generated answer. It researches claims with configured providers, shows the evidence and its dates, and builds a cited answer as of the check. It is evidence-based, not a guarantee of truth.”
**Recording gate:** Confirm the header and `/api/v1/health` both say `live` before recording.

### 0:20-0:50 | Scenario A: stale version and stable fact
**Paste into Workspace:**

> The latest stable release of Python is 3.9. Python was created by Guido van Rossum.

**Point at:** The two claim cards and their status badges. Read the actual status, freshness, and confidence from `scenario_a.json`; do not pre-script an outcome.
**Say:** “Each sentence is evaluated as its own claim. The first is a time-sensitive version claim; the second is a stable attribution. The badges and scores here are the actual result from this run.”

### 0:50-1:20 | Dates and evidence
**Paste:** Nothing; expand the evidence for Scenario A.
**Point at:** Source domain, stance, publication date, retrieved time, and excerpt. If any source date is missing, point at **Freshness: Not established**.
**Say:** “A missing publication date means the app cannot establish freshness from that source. It is not proof that the claim is false. The evidence panel lets us inspect what was retrieved and when.”
**Use only if true in the saved result:** “This source has no publication date, so freshness is not established for this claim.”

### 1:20-1:50 | Scenario B: leadership and landmark claims
**Paste into Workspace:**

> OpenAI's CEO is Sundar Pichai. The Eiffel Tower is in Paris.

**Point at:** Both cards, then expand evidence. Read the real statuses and source stances from `scenario_b.json`.
**Say:** “This pair checks how the current judge handles named-entity claims. A conflict is shown only when the saved result actually reports disagreeing evidence; otherwise I’ll describe the result as insufficient or inconclusive rather than calling it a conflict.”

### 1:50-2:20 | Scenario C: editable product claim
**Paste into Workspace:** The Scenario C text in `inputs_for_video.txt`, after replacing both bracketed fields with values checked immediately before recording.
**Point at:** The product claim badge, evidence dates, and sources. Read the actual values from `scenario_c.json`.
**Say:** “This is an editable example about a product’s price and release. I replaced the placeholders with current values before this run. The result is tied to the sources and dates visible here.”

### 2:20-2:45 | Answer changes and report
**Paste:** Nothing.
**Point at:** Original vs verified answer, highlighted changes, then **Copy verified answer** and **Export report (.md)**. Open the exported report briefly.
**Say:** “The comparison makes changed or qualified text visible. I can copy the verified answer or export the cited Markdown report for review.”

### 2:45-3:00 | Developer Center and caveat
**Paste:** Nothing.
**Point at:** Developer Center endpoint list and error documentation.
**Say:** “The Developer Center documents the API routes. Results depend on available evidence and the configured judge. The built-in heuristic mainly compares numbers and versions; semantic judging requires a configured compatible LLM.”

## Shot list

| Scene | Screen | Action | Duration |
|---|---|---|---:|
| 1 | Workspace | Show live indicator and introduce the workflow | 20 sec |
| 2 | Workspace, Scenario A | Paste answer; inspect the two claim badges | 30 sec |
| 3 | Evidence panel | Expand a claim; show dates and freshness handling | 30 sec |
| 4 | Workspace, Scenario B | Paste answer; show real evidence stances; call a conflict only if reported | 30 sec |
| 5 | Workspace, Scenario C | Paste edited product paragraph; inspect evidence | 30 sec |
| 6 | Original vs verified | Show diff, copy answer, export and open report | 25 sec |
| 7 | Developer Center | Show endpoints and state limitations | 15 sec |

## Pre-recording checklist

- Browser zoom is 100 percent; dark mode is enabled.
- Notifications are off and unrelated windows are closed.
- The server is running and `/api/v1/health` reports `mode: live`.
- `/ui/config` reports `tavily_configured: true` and `llm: openai-compatible`.
- API keys are not visible on screen; close any `.env` editor tab.
- `inputs_for_video.txt` is open in a private editor window and the Scenario C placeholders are replaced with freshly checked values.
- Run all three scenarios once and save each real JSON response and Markdown report in this folder.
- Read the saved JSON while recording; do not claim a status, score, date, correction, or conflict that is not present there.
- Do one complete test run first, including copy and report export.

## 30-second backup script

“TruthGuard extracts factual claims from an answer, researches them with its configured providers, and shows claim-level status, evidence, and publication dates. Freshness is not established when the available evidence has no usable date. The original-versus-verified view highlights changes, and I can copy the result or export a Markdown report. These are evidence-based checks, not guarantees; the built-in judge is heuristic, while semantic judging needs a configured LLM.”

## Likely judge questions

- **Does a stale badge prove a claim is false?** No. It signals that available evidence suggests the claim may be outdated or contradicted; review the sources and dates.
- **What does “Freshness: Not established” mean?** The available evidence did not support a reliable freshness score, commonly because publication dates were missing. It is not a truth score.
- **How does the built-in judge compare claims?** It primarily compares numbers and version tokens. Configure an OpenAI-compatible LLM for semantic evidence judging.
- **What storage and ingestion are supported?** SQLite storage is included. URL/document ingestion is not implemented.
- **How is rate limiting handled?** It is in-memory and per process, so it is not shared across multiple workers or instances.
- **Are sources guaranteed correct?** No. The app presents available sources at check time; evidence quality and coverage vary.
