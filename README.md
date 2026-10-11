# Lenny Growth Assistant

A local-first workspace that turns Lenny's Podcast transcripts into cited answers, Ship 30
essays, and reusable Markdown/HTML briefs. Inspect the underlying passages beside the chat.

React/Vite/TypeScript → FastAPI → PostgreSQL/pgvector, with a real Pi Coding Agent session
using Ollama or explicitly selected Anthropic. HTML is sanitized and sandboxed.

**Final verification is in progress.** The local corpus contains 276 eligible episodes after
provenance checks. Earlier failures remain in reports; `reports/evaluation-final.json` records
the corrected runtime against all 25 declared cases. Read its status before citing results.
See [assessment review](docs/assessment-review.md), [runbook](docs/runbook.md) and `reports/`.

## Host setup (PowerShell)

Prerequisites: Python 3.11+, Node 22.19+ (Node 24 works), Docker Desktop, Ollama, and network
access to GitHub/npm/PyPI/model downloads. Keep an existing `.env`.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python -m pip install -c requirements.lock -e .
npm.cmd --prefix apps/agent ci --ignore-scripts
npm.cmd --prefix apps/web ci
git clone --depth 1 https://github.com/ChatPRD/lennys-podcast-transcripts.git data/raw/lennys-podcast-transcripts
ollama pull nomic-embed-text
ollama pull llama3.2:3b
ollama create lenny-local -f models/Modelfile
docker compose up -d db
$env:DATABASE_URL = 'postgresql+psycopg://postgres:postgres@localhost:55432/lenny'
$env:OLLAMA_BASE_URL = 'http://localhost:11434'
python -m alembic upgrade head
python -m packages.retrieval.ingest --limit 10
python -m packages.retrieval.audit
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

Skip cloning if sources already exist under `data/raw`. Record the corpus commit with
`git -C data/raw/lennys-podcast-transcripts rev-parse HEAD` when using a clone. An extracted
archive may lack commit metadata; disclose that instead of inventing a revision.
Run ingestion without `--limit` to cover the full corpus; unchanged sources are skipped.
Invalid files are reported and produce a nonzero exit while successfully indexed episodes
remain available; inspect the source audit rather than treating rejected files as valid data.
Some upstream metadata conflicts and identical bodies with different source URLs are deliberately rejected. Run the audit after ingestion.
Do not index and generate concurrently on a constrained CPU machine.

In a second terminal, run `npm.cmd --prefix apps/web run dev` and open
[the workspace](http://localhost:5173). To serve the built UI from FastAPI instead, run
`npm.cmd --prefix apps/web run build` before starting the API and open port 8000.

## Container path

`make dev` builds the frontend and Python/Node API image, then starts API and PostgreSQL.
Ollama remains on the host. The intended UI URL is http://localhost:8000.
`make ingest` runs the separate ingestion service against mounted `data/raw`.
The standard image built successfully on 11 October 2026, installing both npm dependency
trees from lockfiles and compiling React inside Docker. An earlier npm failure is preserved
in the development notes. If your network blocks npm during image builds, this explicit
prebuilt alternative remains available:

```powershell
npm.cmd --prefix apps/web ci
npm.cmd --prefix apps/web run build
docker run --rm -v "${PWD}/apps/agent:/app" -w /app nikolaik/python-nodejs:python3.11-nodejs22-slim npm ci --ignore-scripts --omit=dev --no-audit --no-fund
docker compose -f docker-compose.yml -f docker-compose.prebuilt.yml up --build -d db api
```

The prebuilt override copies those Linux-installed agent packages and the compiled frontend.
Rebuild the frontend after UI edits. `docker-compose.dev.yml` is an optional source-mount
override; avoid mounting Windows node_modules into a Linux runtime. The normal Dockerfile
installs from lockfiles and does not require these prebuilt files.

## Configuration

| Variable | Purpose |
|---|---|
| DATABASE_URL | Container: db:5432; host: localhost:55432 |
| OLLAMA_BASE_URL | Host Python connection, normally http://localhost:11434 |
| OLLAMA_BASE_URL_DOCKER | Container connection, normally http://host.docker.internal:11434 |
| OLLAMA_MODEL | Default lenny-local: llama3.2:3b with a 12,288-token context |
| OLLAMA_EMBED_MODEL | nomic-embed-text; schema requires 768 dimensions |
| LLM_PROVIDER | ollama or anthropic |
| ANTHROPIC_API_KEY / ANTHROPIC_MODEL | Both required to enable cloud selection |
| MODEL_TIMEOUT_SECONDS | Default 900; set according to hardware |
| MAX_COSINE_DISTANCE | Default 0.35, requires corpus-specific calibration |
| NODE_BINARY | Node executable, default node |

Store keys in ignored `.env`. OpenAI settings are reserved, not integrated. Cloud selection
sends the question, bounded recent history and retrieved excerpts to Anthropic. No silent
fallback occurs. A credentialed cloud call has not been verified.

The named local model is necessary: Pi reserves 4,096 tokens for context safety. The default
4,096-token Ollama window leaves no output budget. `models/Modelfile` configures 12,288 tokens;
the adapter explicitly uses Ollama’s documented `max_tokens` field. When selecting another
local model, configure at least the same context size and rerun evaluation.

Python application dependency versions are constrained in `requirements.lock` from the
working container. npm dependencies use committed lockfiles. Platform-specific wheels are
resolved by pip on the target platform.

## Validation

```powershell
make test
make lint
npm.cmd --prefix apps/web run build
make eval
```

`make test` runs pytest, the real Pi transport integration test and Vitest.
Windows may require GnuWin32's bin directory on PATH for make. Equivalent backend commands
are `python -m pytest tests/ -v` and `python -m ruff check .` / `python -m mypy apps packages`.
`make eval` runs all 25 live Ollama cases and writes `reports/evaluation.json`; this can take
considerable time on CPU. `make eval EVAL_ARGS="--limit 1 --output reports/smoke.json"` is a
partial smoke run and exits nonzero deliberately. Review claims against passages manually.

API docs: http://localhost:8000/docs. Health/config/library endpoints reveal readiness,
model and eligible corpus size. Migrations run at container startup. Keep database volumes;
do not delete them to troubleshoot connectivity.

## Handoff

[PRD](docs/PRD.md) · [Architecture](docs/architecture.md) · [Design](docs/design.md) ·
[Decisions](docs/decisions.md) · [Security](docs/security.md) · [Runbook](docs/runbook.md) ·
[Development logs](agent-transcripts/2026-10-09.md)

This is a single-user localhost demo. Authentication is required before shared hosting.
The assessment also requires a short camera-enabled demo video, recorded by the applicant.
