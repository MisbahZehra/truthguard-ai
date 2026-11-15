# API
Base `/api/v1`, header `X-API-Key`. OpenAPI UI: `/docs`.
| Method | Path | Notes |
|---|---|---|
| POST | /verify | body `{answer (10-8000 chars), as_of?, max_results?, max_claims?}` |
| POST | /verify/batch | `{items:[...]}` 1-10, independent |
| GET | /verify/{id} | stored result |
| GET | /verify/{id}/report | Markdown report |
| GET | /claims/{id}:{claim_id} | claim evidence |
| GET | /history?q=&status=&since= | sessions |
| GET | /health | no auth |
Errors: `{"error":{"code","message","request_id"}}` with 401/404/422/429(Retry-After)/500. Rate limit `RATE_LIMIT_PER_MIN` per key.
