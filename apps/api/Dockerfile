# Standard reproducible build. The prebuilt alternative is documented in README.
FROM node:22-alpine AS frontend
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

FROM nikolaik/python-nodejs:python3.11-nodejs22-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app
COPY --from=frontend /web/dist apps/web/dist
COPY apps/agent/package.json apps/agent/package-lock.json apps/agent/
RUN cd apps/agent && npm ci --ignore-scripts --omit=dev --no-audit --no-fund
COPY pyproject.toml README.md alembic.ini requirements.lock ./
COPY apps/__init__.py apps/
COPY apps/api/ apps/api/
COPY apps/agent/bridge.mjs apps/agent/
COPY packages/ packages/
COPY alembic/ alembic/
RUN pip install --no-cache-dir -c requirements.lock .
EXPOSE 8000
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn apps.api.main:app --host 0.0.0.0 --port 8000"]
