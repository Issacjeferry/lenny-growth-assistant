# Agent Guidelines & Rules

## Project Overview
**Lenny Growth Assistant** — FastAPI + PostgreSQL + pgvector + Ollama/Claude + React frontend.

## Tech Stack
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic for migrations.
- **Database:** PostgreSQL 16 with pgvector extension.
- **Embeddings:** Ollama nomic-embed-text.
- **Local LLM:** Ollama with llama3.1:8b (or a documented fallback).
- **Cloud LLM:** Anthropic Claude (optional), OpenAI (optional).
- **Frontend:** React with Vite and TypeScript.
- **Testing:** pytest for backend, Vitest for frontend.
- **Containerization:** Docker Compose.

## Core Rules

1. **API Endpoints & Errors:**
   - All API endpoints must use Pydantic models and return structured errors.

2. **Security & Artifact Rendering:**
   - All artifact HTML must be sanitized and rendered in a sandboxed iframe with no `allow-same-origin`.
   - Never commit secrets. Use `.env.example` with safe defaults.

3. **Testing:**
   - Every module must have tests. Use pytest.

4. **Structured Logging:**
   - Logs must be structured JSON with `request_id`, `session_id`, `model`, `latency_ms`, and `error_code`.

5. **Standard Commands:**
   - Use `make dev`, `make test`, `make ingest`, `make eval` as the standard commands.

6. **Scope Discipline:**
   - Do not modify files outside the requested scope.

7. **Grounding & Citations:**
   - Every grounded answer must include at least one citation with episode title and source URL. If retrieval returns no relevant chunks, the agent must refuse and say so explicitly.

8. **Frontend Framework:**
   - Use React with Vite and TypeScript. Do not switch frameworks without explicit approval.
