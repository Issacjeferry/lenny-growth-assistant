# Artifact and agent security

This is an unauthenticated localhost prototype. UUIDs separate conversation histories;
they are not authorization. Do not expose the service to untrusted users without adding
authentication and ownership checks. Compose API/DB published ports bind to localhost.

## HTML boundary

Generated HTML goes through nh3 with an explicit semantic-tag/attribute allowlist.
Scripts, event handlers, forms, frames, SVG/MathML, links, images, embedded objects and
model-supplied metadata are removed. CSS and semantic document content are allowed.
The application, not the model, adds the outer document and its CSP before generated content:

```
default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; form-action 'none'; base-uri 'none'
```

The React viewer uses `sandbox=""` and `referrerPolicy="no-referrer"`. It never adds
`allow-same-origin` or `allow-scripts`. Sandbox blocks script execution and privileged
navigation; CSP blocks resource loads, including CSS URLs/imports. **Sandbox alone does
not block outbound resource requests.** Styles may affect only the isolated frame, not
the host application. Sanitation does not guarantee visually trustworthy content.

Markdown uses a small React renderer that escapes raw HTML, with headings, lists, emphasis
and code. It does not execute HTML or render remote images. Source links outside the iframe
accept credential-free HTTPS URLs and open with `noopener noreferrer`.

Tests cover scripts, event handlers, SVG, iframes, refresh metadata, forms and javascript URLs.
Browser verification of CSP resource blocking, parent isolation and malformed-HTML payloads
is still required before claiming the viewer is verified secure.

## Agent and data boundaries

Pi is intended to run with no built-in tools and no project/plugin resource discovery.
The application owns prompts and supplies bounded retrieved text. Transcript content is
untrusted evidence, not operational instructions. The Pi setup itself still needs a real
installed-runtime check. Subprocess timeouts terminate generation; stderr is not returned
to callers. No public user can choose a executable path through the API.

Only explicit cloud selection sends context to Anthropic. Local generation does not silently
fail over. Request IDs are UUIDs; unexpected errors do not expose exception strings.
Application logs must not include prompts, transcript bodies or API keys. Required JSON log
fields are present, with null values when the information does not apply.

Remaining hardening: rate limits, request body limits, bounded concurrent generation,
authentication/authorization, dependency lockfiles and browser-level adversarial testing.
