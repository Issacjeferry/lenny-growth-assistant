# Interface design

The workspace uses a dark green navigation rail, a warm neutral reading surface and restrained
serif headings. Sources and artifacts sit beside the conversation so a PM can inspect evidence
without losing their question. The design favors readable documents over a dense dashboard.

## Layout and flows

- Sidebar: new conversation, saved sessions, indexed-library count and readiness state.
- Main area: prompt starters, conversation, provider selection and four explicit output modes.
- Inspector: evidence passages with episode links, or artifact preview/source/export controls.
- Narrow view: collapsible navigation and stacked workspace; verify keyboard access and overflow
  using the manual checklist in runbook.md.

A starter fills the composer. Sending shows the pending question and elapsed generation time.
The app displays a validated complete answer, not a simulated token stream. Failure retains the
input for retry and shows a request reference. Switching chats is disabled during a pending turn
so the response stays associated with the correct conversation.

Clicking a source opens the evidence inspector. Citation labels are local to each response.
A title and link establish provenance; users still need to judge whether the passage supports
an individual claim. Timestamp links are available where the transcript has timestamps.

HTML uses a sandboxed iframe with no permissions and a restrictive CSP. Markdown is rendered
with a small React renderer; raw HTML is text. Source view and export make generated work reusable.
An essay outside the target range is visibly marked for review rather than presented as finished.

## State and accessibility requirements

Check initial loading, empty library, ready, pending, explicit refusal, model failure, retry,
artifact preview/source and restored sessions. Native buttons/selects and labeled text areas
support keyboard use. Visible focus, contrast, mobile layout and screen-reader announcements
need manual verification; do not claim WCAG conformance from unit tests alone.

Cloud generation is only offered when configured and selected explicitly. The provider/model
must stay visible; a local failure never silently switches processing to a cloud provider.
