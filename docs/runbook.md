# Operator runbook

Follow README for the standard container, prebuilt override, or host development path.
Both the standard lockfile-based Docker build and the prebuilt alternative succeeded.
Do not remove a database volume to fix a connection issue.

| Symptom | Check / recovery |
|---|---|
| GitHub/npm connection resets | Use an allowed network; retry the README install/clone commands |
| Database password failure on localhost:5432 | This project uses 127.0.0.1:55432; 5432 may belong to host PostgreSQL |
| Ollama down inside Docker | Set OLLAMA_BASE_URL_DOCKER=http://host.docker.internal:11434; check host Ollama |
| Health says missing_models | Check ollama list; pull llama3.2:3b and nomic-embed-text, then ollama create lenny-local -f models/Modelfile |
| Library shows zero episodes | Apply migrations, clone corpus and run ingestion with host DB/Ollama URLs |
| AGENT_UNAVAILABLE / GENERATION_FAILED | Verify Node >=22.19 and apps/agent dependencies; test selected model |
| One-token output / excessive short drafts | Recreate lenny-local from models/Modelfile; Pi needs more than a 4,096-token context |
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

Read reports/evaluation-final.json and review claim support before claiming acceptance.
The standard Docker build is verified; a credentialed cloud call remains applicant-dependent.
Finish the manual UI checks and record the required camera-enabled demo. Lockfiles, the
evaluation harness and full Compose packaging are now implemented; implementation alone
is not acceptance evidence.

## Verified UI checks — 11 October 2026

The packaged homepage loaded with Ready state and 286 episodes / 13,638 passages.
The updated UI was inspected at 390×844: no horizontal overflow (scroll width = 390),
readable stacked output cards, accessible composer and working conversation-menu toggle.
The viewport override was reset after testing. Screenshots are under reports/screenshots.
This is not a complete accessibility certification or browser XSS penetration test.

## Recording checklist

Keep the camera visible. Prepare saved local generations before recording if CPU inference
exceeds the 2–3 minute recording window, and label them as saved results. Show the actual
local model badge, a source passage and timestamp link, follow-up context, independent
sessions, a complete essay, HTML preview/source/export and a genuine refusal. End with
measured evaluation results and the main tradeoff. Do not claim the cloud call was tested
until a credentialed request succeeds. The applicant records and uploads the video.

## Packaged verification — 11 October 2026

The standard multi-stage Docker image built, started and reported health OK with `lenny-local`.
API restart preserved exact conversation/message/artifact responses; stored user metadata also
matched. A real HTML artifact opened beside chat, Source/Preview toggled, and its downloaded
file matched stored content byte-for-byte (SHA-256 in the browser verification notes).
The earlier 286-episode screenshot predates the stricter audit; current count is 276/13,120.

The full evaluation meets the Q&A count and all refusal cases, but failed the essay/artifact
gates. Treat targeted reruns as targeted evidence, not a replacement full benchmark. Inspect
editorial quality and source attribution before choosing outputs for the recording.
