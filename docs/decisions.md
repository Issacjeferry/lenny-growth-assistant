# Architecture decisions

## 2026-10-09 — Runtime and boundaries

1. Use the real Pi Coding Agent session SDK through a bounded Node subprocess. FastAPI handles
   retrieval and deterministic routing. Pi has no active tools, discovered project instructions,
   extensions or persistent credential/session store. This satisfies the specified agent runtime
   without giving transcript content shell access.
2. No automatic cloud fallback. Provider selection is explicit; Anthropic receives source excerpts
   and recent history only when selected. OpenAI settings do not imply a working integration.
3. Embedding outages are structured service errors, distinct from no-evidence refusals.
4. Validate source identities before displaying complete output. Atomic responses simplify safe
   persistence but increase perceived latency; show elapsed time honestly.
5. Sanitize HTML with nh3, inject application-owned CSP, and render in an empty sandbox iframe.
6. Content/configuration hashes allow transactional episode replacement. Source offsets and
   timestamps preserve traceability. Bind database port 55432 to avoid host PostgreSQL conflicts.

## 2026-10-10 — Corpus and verification

7. Keep one canonical indexed record per transcript path and quarantine detectable source metadata
   conflicts. Do not guess corrected titles/URLs or delete raw corpus files. Audit eligibility is
   separate from stored history, so existing citations remain inspectable.
8. Use llama3.2:3b as the default CPU-friendly fallback from llama3.1:8b. The earlier 15–40-second
   estimate was not an end-to-end measurement. A real supported-query smoke run took 294.95 seconds
   and failed with a refusal; it is recorded as a failure, not a successful benchmark.
9. Evaluation keeps HTTP/model failures in the denominator, verifies explicit refusal status,
   checks artifact type and essay length, and never calls a partial run a full pass. Citation
   presence alone cannot establish semantic accuracy.
10. Production packaging builds React and bundles Node/Pi with FastAPI. A clean Docker build failed
    during npm installation on this network. Host development remains the available fallback;
    packaging must be verified on a network where dependency installation succeeds.
