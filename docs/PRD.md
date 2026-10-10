# Product requirements

The user is a growth PM who needs to turn podcast advice into a defensible decision or a
usable draft. The product should shorten the path from a question to an inspectable source,
then to a document they can reuse. Its differentiator is visible evidence and honest failure
handling, supported by a working local agent rather than generic unsupported advice.

## Included experience

- Independent, persistent chats with timestamps and optional user metadata.
- Source-backed Q&A and follow-ups, with episode title, link, passage and available timestamp.
- An explicit refusal when indexed evidence cannot support an answer.
- A dedicated Ship 30 skill producing approximately 1,250 words (acceptance: 1,100–1,400).
- Markdown and complete HTML/CSS artifacts, previewed beside the conversation and exportable.
- A visible provider/model, mandatory Ollama path and optional explicit Anthropic choice.
- Readiness, pending, error, retry and empty-library states.

## Acceptance gates

| Gate | Required evidence |
|---|---|
| Working local agent | Real Pi SDK + Ollama request with cited response |
| Useful grounding | 25-case evaluation, at least 12/15 supported cases; human claim review |
| Refusal | All five unsupported/adversarial cases explicitly refuse without fabricated sources |
| Writing | Both essay cases meet length, readable progression and source support |
| Artifacts | All three artifact cases produce correct type; HTML sandbox and sanitizer tests |
| Persistence | Reload/restart preserves independent conversations and artifacts |
| Cloud | Configured Anthropic path; genuine credentialed smoke test before claiming verification |
| Operability | Fresh setup, migrations, documented configuration and actionable failures |
| Quality | Backend/frontend tests, static checks and manual responsive/keyboard review |
| Handoff | Accurate README, PRD/design/architecture, real development logs, camera-enabled demo |

Citation existence is not a measurement of factual accuracy. Automated scores are structural;
review source entailment separately. Errors remain in evaluation denominators. A partial run
cannot pass the full benchmark. Current measured results are in reports and the runbook.

## Constraints and tradeoffs

Single-user localhost demonstration; authentication, public hosting, web search, billing and
arbitrary agent tools are out of scope. Sources are only the indexed official transcripts.
Provider changes are explicit because cloud selection sends excerpts and recent history.
Responses are atomic after validation, with an elapsed-time state while generation runs.

The initial p95 <8-second local target was unrealistic for the available CPU. Record actual
completion latency and hardware instead of asserting that target. First setup includes model
and dependency downloads plus indexing; do not promise a ten-minute cold setup. A larger
model or a GPU may improve output and latency, but requires re-evaluation.

## Submission priorities

Correct evidence and functioning agent flow come first, followed by artifact utility,
reproducibility and a concise demo. Do not add decorative features at the expense of these
requirements. Keep failures visible and distinguish implemented features from verified ones.
