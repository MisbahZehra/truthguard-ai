# Installation
Requirements: Python 3.11+, Node 20+.
```bash
cp .env.example .env            # add TAVILY_API_KEY for live mode
cd backend && pip install -r requirements.txt && python -m pytest -q
cd ../frontend && npm install && npm test && npm run build
cd ../backend && STATIC_DIR=../frontend/dist uvicorn app.main:create_app --factory --port 8000
# open http://localhost:8000
```
Dev with hot reload: run uvicorn on :8000, then `cd frontend && npm run dev` (proxies /ui and /api).
Docker: `docker compose up --build` (not verified in the build environment).
