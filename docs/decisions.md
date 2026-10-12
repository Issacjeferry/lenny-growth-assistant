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

## 2026-10-11 — Measured runtime corrections

11. A real Pi transport test exposed a one-token output budget: Pi subtracts 4,096 safety
    tokens, equal to our old context configuration. Configure a named local model with
    12,288 tokens and explicitly send Ollama's supported max_tokens field. Keep the original
    model untouched. The test verifies actual SDK request serialization and no active tools.
12. Reject plain text masquerading as HTML; make one bounded format correction and otherwise
    return an actionable error without persisting a partial turn. An essay outside the target
    receives a review status after one bounded length revision. Structural checks are not
    semantic verification, and editorial failures remain recorded.
13. Exclude identical timestamped bodies with conflicting source URLs. The updated audit
    leaves 276 eligible episodes and 70 quarantined records, preserving all raw/history data.
14. The standard multi-stage image now builds successfully with npm lockfile installs.
    Copy the completed frontend stage before installing agent dependencies so these installs
    are ordered. This success does not establish the precise cause of the earlier npm failure.

## 2026-10-12 — Bounded generation recovery

15. Replace six essay turns with one full draft (3,000-token budget). Both six-turn live
    cases timed out. One optional revision receives the actual draft and the remaining
    deadline; failures or worse word counts cannot discard the cited first draft.
16. Prefer explicit full guest names within already-eligible retrieved candidates. Do not
    lower the distance threshold or equate a name match with evidence of claim support.
17. Use IPv4 loopback in host setup: a local `localhost` database connection stalled,
    while `127.0.0.1` connected successfully. Docker retains its service-name addressing.
