FROM node:22-slim AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
RUN npm run build

FROM python:3.12-slim
WORKDIR /srv
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app app
COPY --from=web /web/dist static
ENV STATIC_DIR=/srv/static DB_PATH=/srv/data/truthguard.db
RUN mkdir -p /srv/data
HEALTHCHECK --interval=30s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/api/v1/health')"
CMD ["uvicorn","app.main:create_app","--factory","--host","0.0.0.0","--port","8000"]
