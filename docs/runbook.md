# Operator runbook

Follow README for the current host-based development path. The complete containerized
deployment is still pending. Do not remove a database volume to fix a connection issue.

| Symptom | Check / recovery |
|---|---|
| GitHub/npm connection resets | Use an allowed network; retry the README install/clone commands |
| Database password failure on localhost:5432 | This project uses localhost:55432; 5432 may belong to host PostgreSQL |
| Ollama down inside Docker | Set OLLAMA_BASE_URL_DOCKER=http://host.docker.internal:11434; check host Ollama |
| Health says missing_models | Check ollama list; pull both llama3.1:8b and nomic-embed-text |
| Library shows zero episodes | Apply migrations, clone corpus and run ingestion with host DB/Ollama URLs |
| AGENT_UNAVAILABLE / GENERATION_FAILED | Verify Node >=22.19 and apps/agent dependencies; test selected model |
| MODEL_TIMEOUT | Check memory/load; shorten request or select and document a smaller Ollama model |
| Cloud choice absent | Set both ANTHROPIC_API_KEY and ANTHROPIC_MODEL, restart API |
| EMBEDDING_UNAVAILABLE | Restore Ollama embedding model; this is not an unsupported-question refusal |
| Supported topic refused | Inspect retrieval cutoff and indexed corpus; calibrate against labeled queries |
| Draft needs review | Generated essay missed word target; revise/retry and inspect claim support |

## Manual acceptance checks

1. At desktop and narrow mobile widths, navigate the app with keyboard only. Check focus,
   readable states, horizontal overflow, textarea labels and evidence-panel close controls.
2. Ask a question with a verified source; inspect the title, passage, citation ID and timestamp.
   Check the passage actually supports the claim, not just that a citation exists.
3. Ask a short follow-up. Start a second chat with a different topic and verify no first-chat context.
4. Restart API and DB (without deleting volumes); reopen each chat and its saved artifacts.
5. Generate an essay; manually count/check the target, progression, useful takeaway and support.
6. Generate HTML and Markdown, inspect preview/source/export, and reopen after a refresh.
7. Inject script, onerror, CSS external URL/import, iframe, SVG and refresh payloads in a test
   artifact. Browser network inspection must show no requests from the iframe. Parent DOM
   and storage must remain inaccessible. Check the saved iframe sandbox attribute is empty.
8. Stop Ollama temporarily, submit, then restore it. Confirm explicit service error and retry
   without a duplicated partial turn. Test a missing cloud key and a model timeout.
9. Run a supported and unsupported query with the real local model. Record exact results,
   elapsed times, hardware, corpus commit/count and model tag; do not substitute mocked tests.

## Before submission

Finish Pi/corpus/frontend verification; add lockfiles and full Compose packaging; implement
and run the golden evaluation; export redacted real agent transcripts; update docs with
measured behavior; perform a fresh-clone setup; record the required camera-enabled demo.
