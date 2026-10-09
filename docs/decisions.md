# Architecture Decisions

- 
# Architecture decisions

## 2026-10-09: implementation checkpoint

1. **Pi Coding Agent is the proposed generation runtime.** The assessment requires Pi or
   Claude Agent SDK. Use Pi's actual session API through a bounded Node subprocess, with
   explicit resource loading and built-in tools disabled. FastAPI handles retrieval and
   deterministic routing. This adds Node to backend packaging; npm installation and real
   runtime verification remain blocked. A written bridge is not yet a verified integration.
2. **No silent cloud fallback.** A configured key alone does not authorize the product to
   change a local conversation's processing destination. UI/API provider selection is explicit.
3. **Fail explicitly on embedding outage.** No relevant corpus evidence and unavailable
   retrieval are distinct states. Keyword-only fallback is deferred until evaluated.
4. **Validate before display.** Return a complete response after checking source IDs; no
   token streaming at this checkpoint. This prevents provisional uncited output but increases
   perceived latency. UI shows elapsed time. Streaming can be added with a provisional state.
5. **Static artifacts.** Server-side nh3 allowlist, app-owned CSP and empty iframe sandbox.
   No scripts, forms, images, external links or embeds inside HTML. Exported HTML retains CSP.
6. **Traceable refresh.** Hash source content and chunk/embedding configuration. Replace one
   episode transactionally; retain exact character offsets and available timestamps.
7. **Port isolation.** Use 55432 on the host for this project's DB to avoid the installed
   PostgreSQL listener on 5432. Container-to-container traffic remains db:5432.
8. **Honest status.** Existing planning diagrams are design intent. Acceptance depends on
   actual corpus/model/browser checks, not documentation or synthetic test counts.
