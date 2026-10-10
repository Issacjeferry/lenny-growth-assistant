# ── Runtime image ─────────────────────────────────────────────────────────────
# Frontend is pre-built on the host (npm run build in apps/web/).
# Agent node_modules are pre-installed on Linux via:
#   docker run --rm -v "$PWD/apps/agent:/app" -w /app \
#       nikolaik/python-nodejs:python3.11-nodejs22-slim \
#       npm install --ignore-scripts --omit=dev --no-audit --no-fund
# Both avoid running npm inside a Docker build layer, which crashes at ~71s
# on this machine due to Docker Desktop resource limits.

FROM nikolaik/python-nodejs:python3.11-nodejs22-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app

# Copy Linux-compatible agent dependencies (installed on Linux via docker run)
COPY apps/agent/node_modules /app/apps/agent/node_modules
COPY apps/agent/package.json apps/agent/package-lock.json /app/apps/agent/

# Install Python dependencies
COPY pyproject.toml README.md alembic.ini ./
COPY apps/api/ apps/api/
COPY apps/__init__.py apps/
COPY apps/agent/bridge.mjs apps/agent/
COPY packages/ packages/
COPY alembic/ alembic/
COPY tests/ tests/
RUN pip install --no-cache-dir .

# Copy pre-built frontend (built on host with: cd apps/web && npm run build)
COPY apps/web/dist apps/web/dist

EXPOSE 8000
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn apps.api.main:app --host 0.0.0.0 --port 8000"]
