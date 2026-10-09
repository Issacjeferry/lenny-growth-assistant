# Product Requirements Document (PRD) — Lenny Growth Assistant

## Discovery Brief

- **Primary user:** A growth PM at a B2B SaaS company.
- **Job to be done:** Turn Lenny's Podcast transcripts into grounded answers, Ship 30 essays, and rendered artifacts without needing to understand prompts, models, or infrastructure.
- **Pain removed:** Hallucinated generic AI answers, manual transcript search, and blank-page drafting.

## Success Metrics

- **Citation Coverage:** At least 80% citation coverage on a 25-question golden eval set.
- **Inference Latency:** p95 latency < 8s on local Ollama, < 4s on cloud.
- **Time to First Run:** A fresh evaluator can clone the repo and run the app in under 10 minutes.
- **Viewer Security:** Zero critical XSS issues in the artifact viewer.
- **Draft Utility:** Ship 30 draft is usable after minor edits in under 15 minutes.

## Assumptions

- Transcripts are available locally in `data/raw/`.
- Evaluator has Docker and Ollama installed.
- Cloud API keys are optional.
- No authentication is required for this engagement.

## Scope

### Included
- Grounded Q&A with citations (episode title and source URL).
- Ship 30 for 30 content skill (~1,250 words, hook, formatting, takeaway).
- Artifact viewer with Markdown and sandboxed HTML/CSS rendering beside chat.
- Session persistence across restarts in PostgreSQL.
- Model toggle between local Ollama (`llama3.1:8b`) and cloud LLM (Claude/OpenAI).
- Secure rendering with HTML sanitization and sandboxed iframe isolation.
- Evaluation harness (`make eval`) evaluating citation coverage and refusal behavior.
- Docker Compose setup and standard developer commands (`make dev`, `make test`, `make ingest`, `make eval`).
- Complete documentation suite (`PRD.md`, `architecture.md`, `design.md`, `decisions.md`, `README.md`).

### Excluded
- User authentication and role-based access control (RBAC).
- Multi-tenant data segregation.
- Billing, subscription, and usage metering systems.
- Model fine-tuning or custom weight training.
- Mobile application (iOS / Android).
- Real-time multiplayer collaboration.
- Administrative dashboard and usage analytics portal.

## Flows

### 1. New Session → Ask Question → Grounded Answer with Citations
1. User clicks "New Chat" in the UI; a new session UUID is initialized via `POST /api/sessions`.
2. User submits a product or growth question.
3. System generates embeddings via Ollama `nomic-embed-text` and performs similarity retrieval in pgvector.
4. Agent receives top matching transcript chunks and generates a response.
5. Response is returned with at least one citation containing episode title and source URL.
6. Messages and session state are persisted to PostgreSQL.

### 2. Request Ship 30 Essay → Agent Retrieves Sources → Generates ~1,250-Word Essay → Renders in Chat
1. User requests a Ship 30 style essay on a growth or product topic.
2. Agent invokes the Ship 30 for 30 skill and retrieves relevant source transcript chunks.
3. Skill applies the Ship 30 framework: strong hook, 1-3-1 rhythm, subheadings, bold emphasis, and a clear takeaway.
4. Agent generates an essay of approximately 1,250 words grounded in transcript facts.
5. Essay renders in the chat feed with citations and an action button to open in the Artifact Viewer.

### 3. Request Artifact → Agent Generates Markdown or HTML → Renders in Artifact Viewer Beside Chat
1. User asks the assistant to create an artifact (e.g., an HTML onboarding checklist, metric calculator, or Markdown framework).
2. Agent outputs an artifact payload specifying title, type (`html` or `markdown`), and raw content.
3. UI detects the artifact payload and opens the side-by-side Artifact Viewer pane.
4. Markdown renders natively; HTML is sanitized via DOMPurify and rendered inside a sandboxed `<iframe>` with `sandbox="allow-scripts"` and strictly no `allow-same-origin`.

### 4. Unsupported Question → Refusal with Explanation
1. User submits an out-of-domain query or a question not covered by the transcripts.
2. Vector retrieval finds no chunks meeting the relevance distance threshold.
3. Agent executes refusal protocol: refuses to answer and explicitly informs the user that the knowledge base contains no relevant information on the topic.
4. No hallucinated or ungrounded claims are generated.

## Acceptance Criteria

1. **API Contracts:** Every API endpoint validates input and output using Pydantic v2 models and returns structured JSON errors (`error_code`, `message`, `request_id`) on failure.
2. **Session Persistence:** All sessions, messages, and timestamps are persisted to PostgreSQL and reliably reloaded upon page refresh or session switching.
3. **Grounding & Citations:** Every supported answer provides at least one citation containing episode title and source URL referencing the transcript knowledge base.
4. **Refusal Behavior:** The system explicitly refuses to answer and outputs zero citations when retrieval yields no relevant chunks above the threshold.
5. **Model Toggle & Fallback:** The user can toggle between local Ollama (`llama3.1:8b`) and cloud LLM (Claude/OpenAI) in configuration/UI, and the system automatically falls back to local Ollama if the cloud provider is unavailable.
6. **Ship 30 Skill Execution:** The Ship 30 skill generates a ~1,250-word structured essay with a hook, subheadings, bullet points, and specific actionable takeaways grounded in transcript evidence.
7. **Artifact Viewer Isolation:** All HTML artifacts render inside a sandboxed `<iframe>` with `sandbox="allow-scripts"` and no `allow-same-origin`, blocking access to parent DOM, cookies, and local storage.
8. **Structured Logging:** All backend requests and model calls emit JSON logs containing `request_id`, `session_id`, `model`, `latency_ms`, and `error_code`.
9. **One-Command Setup:** Running `docker compose up` starts PostgreSQL (pgvector), Ollama, FastAPI backend, and React frontend in under 10 minutes on a clean machine.
10. **Evaluation Benchmark:** Executing `make eval` runs a 25-question golden benchmark achieving >= 80% citation coverage and 100% refusal on unsupported queries.

## Risks and Trade-offs

- **Hallucination**
  - *Risk:* LLM produces fabricated advice not present in the transcripts.
  - *Mitigation:* Strict RAG grounding prompt instructions, similarity threshold cutoff, mandatory source citation extraction, and deterministic refusal fallback.
- **Latency**
  - *Risk:* Local inference with Ollama on consumer hardware can exceed acceptable response times.
  - *Mitigation:* Token streaming via Server-Sent Events (SSE), optimized context chunk count (top-k = 4–6), and lean system prompts.
- **Cost**
  - *Risk:* Excessive API token bills when using cloud models for long-form generation.
  - *Mitigation:* Local-first default (Ollama free of cost), token caching, and user-initiated cloud model toggle.
- **Local-Model Quality**
  - *Risk:* 8B local models may struggle with strict JSON schema adherence or long 1,250-word structured essays.
  - *Mitigation:* Clear few-shot framing, deterministic post-processing validators, and graceful fallback to cloud models when configured.
- **Data Leakage**
  - *Risk:* Accidental exposure of API keys, environment secrets, or session data across user queries.
  - *Mitigation:* Safe `.env.example` defaults, strict git-ignore policies, stateless API request lifecycle, and session-partitioned database queries.
- **Unsafe Artifact Rendering**
  - *Risk:* Malicious or malformed HTML/JS artifacts performing Cross-Site Scripting (XSS) or stealing parent session context.
  - *Mitigation:* Client-side DOMPurify sanitization and rendering inside an `<iframe>` configured with `sandbox="allow-scripts"` and strictly no `allow-same-origin`.

## Implementation Plan

- **Phase 0: Foundation & Standards**
  - Repository structure, `.env.example`, `AGENTS.md`, `Makefile`, and Docker Compose scaffolding.
  - Structured JSON logging setup and Pydantic base error models.
- **Phase 1: Knowledge Ingestion & Vector Storage**
  - Ingestion pipeline parsing transcripts in `data/raw/` into metadata-tagged chunks.
  - Embedding generation using Ollama `nomic-embed-text`.
  - PostgreSQL schema and `pgvector` index creation via Alembic migrations.
  - CLI command `make ingest` with idempotent processing.
- **Phase 2: RAG Pipeline, Agent Core & Model Toggle**
  - Semantic retriever with cosine similarity threshold and metadata filtering.
  - LLM provider abstraction supporting Ollama (`llama3.1:8b`) and Cloud (Claude/OpenAI) with runtime toggle and fallback.
  - Grounded prompt templates with mandatory citation enforcement and refusal handling.
  - FastAPI endpoints for sessions, messages, and streaming chat completions.
- **Phase 3: Ship 30 Skill & Artifact Generation**
  - Ship 30 for 30 essay generation skill prompt and structure validator.
  - Artifact extractor detecting and formatting Markdown and HTML/CSS snippets.
  - Server-side artifact payload validation.
- **Phase 4: Frontend & Sandboxed Artifact Viewer**
  - React + Vite + TypeScript application setup.
  - Chat interface supporting streaming responses, citation chips, and session navigation.
  - Side-by-side Artifact Viewer with Markdown renderer and sandboxed `<iframe>`.
  - Model toggle selector and connection status indicators.
- **Phase 5: Evaluation & Quality Assurance**
  - 25-question golden benchmark dataset creation (`tests/eval/`).
  - Automated evaluation harness executed via `make eval`.
  - Backend unit/integration tests with `pytest` and frontend tests with `Vitest` executed via `make test`.
  - XSS security testing on the artifact viewer.
- **Phase 6: Deployment, Observability & Handoff**
  - Multi-container Docker Compose verification (`make dev`).
  - System architecture documentation (`docs/architecture.md`) and UI design guide (`docs/design.md`).
  - Operational handoff documentation, troubleshooting guide, and demo walkthrough.
