# Submission strategy and gap review

Reviewed 9 October 2026 against the supplied assessment and the actual working tree.
This is our analysis, not an official scoring system. No rubric weights or selection
probability were supplied. A compelling submission can improve the evidence of ability;
it cannot guarantee selection among other candidates.

## What evaluators need to see

| Evaluation area | Demonstration that makes it credible |
|---|---|
| Customer and product judgment | One concrete growth-team workflow, measurable outcomes, explicit exclusions |
| Technical execution | A real conversation travels through React, FastAPI, PostgreSQL, retrieval and the required agent runtime |
| Agent architecture and grounding | Dedicated skills, correct follow-up context, inspectable sources, honest refusal and failure states |
| Deployment and operability | Fresh-clone startup, visible provider/model, understandable errors and a usable runbook |
| Code quality | Clear modules, typed boundaries, meaningful failure and persistence tests |
| UI/UX | A coherent workspace with readable answers, accessible controls, evidence and artifacts beside chat |
| Communication | Brief rationale, measured limitations, genuine development logs and a clear live demo |

## Product differentiation: evidence to action

Target one user: a B2B SaaS growth PM deciding what to test next.
The signature flow is **question → inspect exact evidence → apply to this team → create a brief**.
Use one conversation for the entire demo. An example starts with evaluating readiness to
scale acquisition, follows up about activation, and produces a cited experiment brief.
Select the exact questions only after checking the indexed corpus supports them.

Show source title, guest, exact retrieved passage and source timestamp when available.
Distinguish a guest's advice from a proposed application. Never label a cosine distance as
a probability that an answer is true. Never generate fabricated citations to make an answer
look grounded. An inspectable citation is still not a semantic fact-check.

Keep the visual design calm: forest sidebar, warm paper workspace, restrained orange
primary action, serif editorial headings and an evidence inspector. Functional clarity
matters more than animations, landing-page decoration or feature count.

## Baseline findings

- Existing FastAPI/settings/logging foundation was useful; no broad rewrite was needed.
- Original five tests passed, but covered health/config rather than product behavior.
- README and assessment-brief files were empty, despite the reported status.
- Agent architecture did not specify either mandated agent runtime.
- At inspection, Ollama listed only `nomic-embed-text`; generation model installation was incomplete.
- No database migration, ingestion, working conversation UI or benchmark existed.
- Original PRD mixed desired behavior with verified capabilities.
- Existing local PostgreSQL also occupied port 5432. Compose now uses localhost port 55432.

## Required corrections and current state

| Requirement | Current state | Remaining proof |
|---|---|---|
| FastAPI and contracts | Implemented; typed endpoints and structured failures | Verified by regression tests |
| PostgreSQL persistence | Isolation/rollback tests; saved messages, artifacts and metadata survive API restart | DB restart not yet exercised |
| Required agent runtime | Real Pi SDK installed/invoked; zero tools; request serialization tested | Credentialed cloud response pending |
| Local demo | Ollama lenny-local (llama3.2:3b, 12,288 context) | Review generated claims |
| Cloud integration | Anthropic adapter and explicit UI selection implemented | API key/model are still absent locally |
| Corpus | 276 eligible episodes / 13,120 passages; 70 quarantined records | Raw snapshot hashes recorded; source commit unknown |
| Grounding | Full run: 12/15 supported, 5/5 refusal cases pass structurally | Semantic accuracy is not established by these scores |
| Ship 30 | Six-section workflow in a single Pi session; bounded revision | Targeted live rerun in progress |
| Artifact viewer | Sanitizer/CSP/opaque iframe; real preview/source/export verified | Targeted live generation rerun in progress |
| Startup | Standard Docker build succeeds from npm lockfiles; packaged health is OK | Verified locally, not on a second clean machine |
| Tests | 50 backend, 5 frontend and 2 Pi transport tests pass | Verification output and development notes retained |
| UI | Mobile layout/source inspector; real HTML artifact preview and export | Full accessibility audit deferred |
| Agent logs | Actual actions/results with failures; reasoning/system noise removed | Review redacted logs before publishing |
| Demo | Camera-enabled recording script and runbook provided | Applicant recording/upload required |

The complete baseline report is `reports/evaluation-final.json`: it **failed overall** because
both essays and two artifacts missed their gates. Several long durations include machine
suspension and cannot establish a useful p95. Subsequent targeted runs are recorded separately;
they must not be relabeled as a fresh full-suite pass. The earlier 1,194-word essay met length
but failed editorial review. See `reports/README.md` for provenance and limitations.

## Scope choices

Keep FastAPI, PostgreSQL/pgvector, React/Vite/TypeScript and local Ollama. Use Pi for both
local and Anthropic generation to satisfy the runtime requirement with one integration path.
Pi's documented SDK supports embedded sessions and explicit model/resource configuration:
https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
Ollama uses Pi's compatible-endpoint configuration:
https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md

Defer a second cloud integration, multi-agent orchestration, billing, admin dashboards,
animated dashboards, authentication for a localhost demo and interactive JavaScript artifacts.
Automatic cloud fallback is removed: users explicitly choose cloud to control data sharing.
Embedding failure returns a service error, not a misleading no-evidence refusal.
Keyword-only fallback is deferred until it has its own calibrated relevance gate.

## Measurable acceptance gates (targets, not reported results)

- Every displayed supported answer identifies real retrieved sources; invalid source IDs are rejected.
- A reviewed 25-case set includes supported questions, follow-ups, comparisons, unsupported queries,
  injection attempts and artifacts. Report valid-ID coverage separately from semantic support.
- Unsupported examples in that declared test set all refuse. Do not generalize that rate to all questions.
- Record first-response and completion latency separately, hardware/model/corpus size, cold/warm
  conditions and individual samples. Choose the latency target after measuring local performance.
- Ship 30 drafts meet approximately 1,250 words, a useful hook and takeaway, and supported claims.
- Restart preserves independent conversations and artifact associations.
- Browser checks show no script execution, parent access or outbound loads from artifacts.
- A fresh evaluator can follow documented prerequisites and startup without undocumented fixes.

## Suggested final demo (150 seconds)

1. 0–20s: camera enabled; explain the PM's decision and show local provider/model and corpus count.
2. 20–55s: ask a prepared but genuine corpus-backed question; inspect one supporting passage.
3. 55–80s: ask a contextual follow-up, then switch sessions to show independent history.
4. 80–115s: open a generated essay and rendered brief; show their source trail and export.
5. 115–135s: demonstrate an unsupported question refusing without invented evidence.
6. 135–150s: explain the local latency/security trade-off and point to runbook and measured evaluation.

Do not imply prerecorded output was generated live. Prepare long local generations before recording
and identify them as saved drafts if needed. The candidate must record the camera segment.
