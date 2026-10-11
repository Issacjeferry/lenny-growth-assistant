# Camera-enabled demo: 2–3 minutes

Use actual saved outputs from this machine. Keep the camera visible. Local inference is
slow on this CPU, so say explicitly when opening a saved generation. Do not imply it is
being generated live. Read the final evaluation report and avoid quoting an unfinished run.

## 0:00–0:20 — The decision

“This is Lenny Growth Assistant, for a growth PM who needs to turn podcast advice into a
decision they can defend. The workflow is question, evidence, then an actionable draft.”

Show the workspace, eligible episode count, and Ollama/local model badge. Explain that
`lenny-local` is llama3.2:3b with a larger context window, running through the real Pi SDK.

## 0:20–0:50 — Inspect the evidence

Open a saved, reviewed Jobs to Be Done answer. Say “I generated this locally before the
recording.” Open a citation and point to the episode title, exact passage and timestamp link.
Explain which specific claim the passage supports. A citation is a way to inspect support,
not a guarantee that every generated sentence is correct.

## 0:50–1:10 — Continue the work

Show a saved contextual follow-up. Switch to a different conversation and back; explain
that PostgreSQL stores independent histories and artifacts. Refresh to demonstrate persistence.

## 1:10–1:50 — Turn evidence into a deliverable

Open a reviewed Ship 30 essay. Show the approximate word count, distinct sections and
takeaway. Then open a generated visual brief beside the conversation, toggle Source/Preview
and export it. Explain that HTML is sanitized, cannot run scripts, and renders in an opaque
sandbox with a policy that blocks resource loads.

## 1:50–2:10 — Show a boundary

Ask “What is the recipe for chocolate chip cookies?” Show the explicit unsupported-answer
refusal. Mention that unavailable search/model services produce a retryable error instead
of being mislabeled as a lack of evidence.

## 2:10–2:40 — Explain the engineering trade-off

“I prioritized inspectable sources, atomic persistence and safe artifacts over a bigger
feature list. The small CPU model is slow and still needs editorial review. I kept failed
evaluations, added a real Pi transport test, and quarantined conflicting corpus metadata.
Anthropic is an explicit opt-in integration; I only claim a real cloud test if credentials
were configured and that request succeeded.”

Show the README, final evaluation status, test log and runbook briefly. Finish with the
single next improvement supported by the results, rather than promising perfect accuracy.

## Applicant-owned final steps

- Configure cloud credentials locally and verify the selected provider if still pending.
- Record the camera segment and screen capture, review for secrets and personal tabs.
- Upload the required video and add its link to the submission. Do not include `.env`.
- Push the reviewed commit and submit the repository/video links yourself.
