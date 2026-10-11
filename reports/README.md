# Verification evidence

These files are measurements and review records, not generated sample success claims.

- `evaluation.json`: original full 25-case failure, retained for comparison. Its extreme
  latencies include machine suspension; do not use it as a controlled performance benchmark.
- `evaluation-final.json`: subsequent full run with the corrected Pi token budget and
  `lenny-local` context, stricter HTML checks, writing instructions and audited corpus.
  Check `status` and case count before calling it complete. Structural passes are not
  semantic accuracy scores.
- `essay-context-fix.json`: one real essay after fixing the adapter, 1,194 words / 453.88s.
  It met the mechanical target but failed editorial review: repetitive sections, an early
  conclusion and a claim about category design attributed to the wrong source. This led
  to stricter writing instructions; it is not presented as a polished final essay.
- `source-audit.json`: 276 eligible records, 70 quarantined records. Quarantine retains
  raw files, historical messages and DB rows; aliases and conflicting provenance are
  excluded from new retrieval.
- `corpus-provenance.json`: SHA-256 inventory of the 303 downloaded transcript files.
  The extracted archive did not identify its source commit, so that field is explicitly null.
- `smoke*.json`, `essay-smoke.json`: earlier failures/partial checks, not full acceptance.
- `screenshots/`: real browser captures. `artifact-isolation.jpg` is clearly identified
  as a synthetic malicious fixture, not a model-generated artifact.

Automated regression output: `agent-transcripts/verification-2026-10-11.log`.
Hardware: Windows 11, Intel Core i5-1335U, approximately 16 GB RAM, CPU inference.
The final run began while a Docker image was building, so latency is an observed workload
measurement, not a controlled model benchmark. Atomic responses mean response completion
and first displayed answer occur together.

## Browser security fixture, 11 October 2026

The fixture used the production sanitizer and an iframe with `sandbox=""` and
`referrerpolicy="no-referrer"`. Injected script/image-event/form/frame content was removed.
The browser reported `Opaque frame: true; parent unchanged: true`. CSS `@import` and
background-image probes pointed at the local test server; after page load its access log
contained only the page request and no requests to either probe URL. Application-owned
CSP appeared before all generated content. This is bounded evidence for these payloads,
not a claim of exhaustive XSS or browser-security coverage.
