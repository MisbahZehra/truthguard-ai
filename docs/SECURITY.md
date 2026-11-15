# Security
- Secrets only in environment variables; never sent to the browser (UI uses `/ui/*`, which holds no key; `UI_ENABLED=false` disables it).
- Input limits (8000 chars), request timeouts, retries with backoff, per-key / per-IP rate limiting.
- Retrieved content is untrusted: HTML stripped, instruction-like phrases neutralized and flagged, content passed to the LLM as data with an explicit system rule; LLM output schema-validated, fabricated URLs and numbers rejected.
- `is_safe_url` SSRF guard (http/https only, blocks private/loopback/link-local). NOTE: URL ingestion is not implemented, so the guard is currently unused by a user-facing feature.
- Key-like tokens and emails are redacted from submitted text before processing and storage.
- SQL uses parameters only. Retention: sessions older than `RETENTION_DAYS` purged at startup.
- Limits: in-memory rate limiting is per-process; `/ui` is open to anyone who can reach the server, so put it behind your network controls for non-demo use. No claim of guaranteed truth is made.
