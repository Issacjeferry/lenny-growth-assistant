# Lenny Growth Assistant

A local-first workspace for turning Lenny's Podcast transcripts into answers, essays,
and reusable briefs, with the underlying evidence visible beside the conversation.

**Status: implementation checkpoint, not submission-ready.** The database migration and
backend tests have local verification. The real Pi/Ollama generation path, corpus retrieval,
frontend build/browser behavior, cloud calls, and fresh-machine setup still need validation.
GitHub/npm downloads were blocked on the development network. See
[the assessment review](docs/assessment-review.md) for the remaining acceptance gates.

## Architecture

React + Vite + TypeScript → FastAPI → PostgreSQL 16 / pgvector.
Ollama `nomic-embed-text` embeds queries and passages. Semantic retrieval gates relevance;
PostgreSQL full-text search and reciprocal rank fusion reorder eligible passages.
FastAPI supplies bounded session history and retrieved evidence to a restricted Pi Coding
Agent subprocess. Pi uses Ollama or explicitly configured Anthropic. There is no automatic
local-to-cloud fallback. HTML passes through `nh3`, then a CSP document and sandboxed iframe.

The current UI offers Q&A, a Ship 30 essay, an HTML brief, and a Markdown document.
Responses are returned atomically after citation checks; token streaming is not implemented.

## Prerequisites

- Python 3.11+, Node 22.19+ (Node 24 is suitable), Docker Desktop and Ollama.
- Network access to GitHub, npm, PyPI and the Ollama model registry for initial setup.
- Enough memory for the selected model; benchmark on your own machine before claiming latency.

## Finish setup on a network with downloads enabled (PowerShell)

Run from the repository root. Keep an existing `.env`; copy the example only if absent.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python -m pip install -e .
npm.cmd --prefix apps/agent install --ignore-scripts
npm.cmd --prefix apps/web install
git clone --depth 1 https://github.com/ChatPRD/lennys-podcast-transcripts.git data/raw/lennys-podcast-transcripts
ollama pull nomic-embed-text
ollama pull llama3.1:8b
docker compose up -d db
$env:DATABASE_URL = 'postgresql+psycopg://postgres:postgres@localhost:55432/lenny'
$env:OLLAMA_BASE_URL = 'http://localhost:11434'
python -m alembic upgrade head
python -m packages.retrieval.ingest --limit 10
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, run `npm.cmd --prefix apps/web run dev`, then open
http://localhost:5173. The first ten episodes are a setup smoke test, not a representative
evaluation corpus. Run ingestion without `--limit` to index everything. Re-running skips
unchanged episodes. Keep the cloned source locally; raw transcripts are gitignored.
Record the source commit with `git -C data/raw/lennys-podcast-transcripts rev-parse HEAD`.

If cloning already succeeded, do not clone again. If `ollama` is missing from PATH on Windows,
its executable may be under `%LOCALAPPDATA%\Programs\Ollama\ollama.exe`.

**Container limitation:** `make dev` currently starts the database and Python API scaffold.
The API Dockerfile does not yet bundle Node/Pi, and Compose does not yet start the frontend.
Use the host development path above for generation until container packaging is completed.
Do not describe the current Compose stack as a complete one-command deployment.

## Configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Compose: `db:5432`; host Python: `localhost:55432` |
| `OLLAMA_BASE_URL` | Host Python connection, normally `http://localhost:11434` |
| `OLLAMA_BASE_URL_DOCKER` | Container connection, normally `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | Local generation model, default `llama3.1:8b` |
| `OLLAMA_EMBED_MODEL` | Embedding model, fixed 768-dimensional schema |
| `LLM_PROVIDER` | Default provider: `ollama` or `anthropic` |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Both required to enable the cloud choice |
| `MODEL_TIMEOUT_SECONDS` | Generation timeout, default 300 seconds |
| `MAX_COSINE_DISTANCE` | Semantic cutoff, default 0.35; not yet calibrated |
| `NODE_BINARY` | Node executable or absolute path, default `node` |

OpenAI variables are reserved and do not represent a working integration. The selected
cloud model ID must be valid for your account. Store keys only in the ignored `.env`.
Explicit cloud selection sends the question, recent conversation, and retrieved excerpts
to Anthropic. Local provider failure returns a structured error; it does not change providers.

## Commands and checks

```powershell
make test
make lint
make ingest
npm.cmd --prefix apps/web run build
npm.cmd --prefix apps/web test
```

On Windows, add `C:\Program Files (x86)\GnuWin32\bin` to this terminal's PATH if needed.
`python -m pytest tests/ -v` is the equivalent backend test command. Host ingestion requires
the host `DATABASE_URL` and `OLLAMA_BASE_URL` overrides shown above.
`make eval` deliberately exits unsuccessfully until the real corpus benchmark is built.
Synthetic unit fixtures are not evidence of retrieval quality or model accuracy.

The HTTP endpoints are documented at http://localhost:8000/docs. Start with `/health`,
`/config`, `/api/library`, and `/api/sessions`. The health endpoint distinguishes an absent
Ollama server from missing local models. Conversations and artifacts persist in PostgreSQL.

## Handoff

- [Assessment review and remaining gates](docs/assessment-review.md)
- [Current architecture](docs/architecture.md) and [decisions](docs/decisions.md)
- [Product requirements](docs/PRD.md) and [interface design](docs/design.md)
- [Security boundaries](docs/security.md)
- [Troubleshooting and manual checks](docs/runbook.md)
- [Development log](agent-transcripts/2026-10-09.md)

This is an unauthenticated local demonstration. It is not a multi-user deployment.
Keep it on localhost. Authentication and authorization are required before shared hosting.
