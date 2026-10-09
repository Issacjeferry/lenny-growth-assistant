# UI/UX Design Specification — Lenny Growth Assistant

## 1. Design Principles

The user interface of the Lenny Growth Assistant is designed for focus, trustworthiness, and effortless artifact utilization.

- **Local-First:** Prioritizes zero-lag, instant UI interactions, snappy local database state loading, and transparent visibility into local Ollama model execution.
- **Clear States:** Eliminates ambiguity with distinct visual representations for every operational phase (idle, sending, streaming tokens, artifact rendering, and errors).
- **Citable Answers:** Builds user trust by elevating source citations to first-class UI citizens rather than tucked-away footnotes; every claim is visibly grounded in an episode and guest.
- **Artifact-First Layout:** Treats long-form essays, frameworks, checklists, and code snippets as tangible objects displayed side-by-side with conversation, not buried within chat bubbles.

---

## 2. Information Architecture

The interface uses a split-screen workspace topology organized into three distinct structural zones.

```text
+---------------------+------------------------------------------+------------------------------------------+
| Left Sidebar        | Main Chat Area                           | Right Pane (Conditional)                 |
| (Session List)      | (Active Conversation & Composer)         | (Artifact Viewer)                        |
|                     |                                          |                                          |
| +-----------------+ | [Chat Header: Episode Topic / Controls]  | [Artifact Header: Title | Close (x)]     |
| | + New Chat      | |                                          |                                          |
| +-----------------+ | [Assistant Message: Grounded response]   | +--------------------------------------+ |
|                     | [Citation Chips: (1) Episode #142]       | | Sandboxed Iframe / Rendered Markdown | |
| * PLG Metrics       |                                          | |                                      | |
| * Onboarding Flow   | [Assistant: Ship 30 Essay]               | | [HTML Wireframe / Essay Draft]       | |
| * Pricing Strategy  | [Button: "Open in Viewer"]               | |                                      | |
|                     |                                          | +--------------------------------------+ |
|                     |                                          |                                          |
| +-----------------+ | +--------------------------------------+ |                                          |
| | Model Badge     | | Composer Input Box                     | |                                          |
| | Ollama (8B) [●] | | [Ask Lenny a growth question...] [Send]| |                                          |
| +-----------------+ | +--------------------------------------+ |                                          |
+---------------------+------------------------------------------+------------------------------------------+
```

### Zone Descriptions
1. **Left Sidebar:**
   - Top: "New Chat" primary button with keyboard shortcut indicator (`Ctrl + N` / `Cmd + N`).
   - Center: Scrollable chronological list of conversation sessions, grouped by time (Today, Yesterday, Previous 7 Days).
   - Bottom: Provider and model indicator badge (e.g., `Ollama · llama3.1:8b`) with live health status dot.
2. **Main Chat Area:**
   - Header: Active session topic title, session export actions, and model indicator.
   - Message Thread: Chronological stream of user messages, assistant responses, inline citation badges, and action triggers.
   - Composer: Sticky bottom input area with multiline support (`Shift + Enter`), auto-resizing text area, and submit button.
3. **Right Pane (Conditional):**
   - Expands dynamically when an artifact is generated or when the user clicks "Open in Viewer" on an existing artifact.
   - Contains title bar, copy code button, raw/preview view switcher, and sandboxed rendering viewport.

---

## 3. Key Screens

### 1. Empty State (No Sessions)
- **Visuals:** Clean, focused hero layout in the main chat pane.
- **Content:**
  - Headline: "Lenny Growth Assistant"
  - Subhead: "Grounded product, growth, and PLG advice from 200+ podcast interviews."
  - Prompt Starters: 4 clickable cards (e.g., "Elena Verna's B2B product-led sales loops", "How Superhuman measures Product-Market Fit", "Synthesize pricing strategies into a Ship 30 essay").
  - Sidebar displays: "No conversations yet. Start a new chat above."

### 2. New Session with No Messages
- **Visuals:** Active session initialized with a fresh UUID. Sidebar highlights "New Chat" as active.
- **Main Area:** Centered placeholder greeting prompting user input, with cursor automatically focused on the message composer.

### 3. Active Conversation with Citations
- **User Message:** Right-aligned speech bubble with clean typography.
- **Assistant Message:** Left-aligned full-width container with rich Markdown formatting (subheadings, bullet points, code blocks).
- **Citations Row:** Displayed immediately underneath assistant text:
  - Visual chips containing episode title, guest name, and external link icon to YouTube.
  - Interactive hover state previews exact timestamp and source quote snippet.

### 4. Ship 30 Essay Rendered in Chat
- **Visuals:** Distinguished block container with subtle border accent and "Ship 30 for 30 Essay" badge.
- **Formatting:** Displays the ~1,250-word structured text adhering to the atomic essay format (Headline Hook, 1-3-1 rhythm, bolded key phrases, bulleted frameworks).
- **Action Button:** "Open in Viewer" floating action button positioned at the top right of the essay card to launch the split pane for focused reading or copying.

### 5. Artifact Viewer Open Beside Chat
- **Visuals:** Chat area smoothly transitions from centered layout to a 50/50 or 60/40 split pane.
- **Artifact Header:** Displays artifact title (e.g., `PLG-Metrics-Calculator.html`), format tag (`HTML` or `Markdown`), and a close `[✕]` button.
- **Viewport:** Renders the content inside an isolated `<iframe sandbox="">` with custom CSS styling and no scripts.

### 6. Error States
- **Provider Unavailable:**
  - Banner alert at the top of the chat: "Local Ollama service unreachable at localhost:11434. Falling back to Claude 3.5 Sonnet..." or "No model provider available. Check your Ollama instance."
- **Retrieval Empty (Refusal):**
  - Assistant card: "I could not find relevant insights in Lenny's Podcast transcripts to answer this question. My knowledge is strictly grounded in the podcast episodes."
  - Zero citations displayed; clear indication of grounding boundary.
- **Network / SSE Error:**
  - Inline retry chip: "Message stream interrupted. [Retry Request]".

---

## 4. Interaction States

### Message States
- **Sending:** User input submitted; composer disables briefly, message bubble appears in thread with a subtle pulsating dot indicator.
- **Streaming:** Server-Sent Events (SSE) stream incoming tokens in real-time with smooth autoscroll down the conversation feed.
- **Done:** Stream completes; citations row fades in, copy buttons activate, and composer re-enables for follow-up questions.
- **Error:** If generation aborts or fails, an error alert banner is attached to the message container with an actionable retry button.

### Citation Chip Interactions
- **Default State:** Subtle pill badge (e.g., `[🎙️ Shreyas Doshi: Good Product vs. Great Product]`).
- **Hover State:** Tooltip popover surfaces the specific 2–3 sentence transcript passage retrieved by pgvector and the YouTube timestamp link.
- **Click State:** Opens the original YouTube source URL in a new browser tab with `rel="noopener noreferrer"`.

### Model Badge & Popover
- **Default State:** Small bottom-sidebar chip with status dot:
  - 🟢 Green: Provider active & responsive (e.g., `Ollama · llama3.1:8b`).
  - 🟡 Amber: Running on cloud fallback provider.
  - 🔴 Red: Provider disconnected or offline.
- **Click State:** Opens a compact popover detailing:
  - Active Provider & Model Name
  - Database connectivity: `Connected (PostgreSQL 16)`
  - Embedding Service: `nomic-embed-text (Ollama)`
  - Direct toggle or link to check `/health` and `/config`.

### Artifact Viewer States
- **Loading:** Displays a skeleton loader with pulsating shimmer while the server sanitizes and packages the artifact payload.
- **Rendered:** Clean, high-contrast rendering within the sandboxed iframe with custom scrollbars and dark/light mode synchronization.
- **Error (Sanitization Blocked):** If the artifact contains invalid markup or blocked exploits, a warning message informs the user: "Potentially unsafe scripts or attributes were detected and stripped during server-side sanitization."

---

## 5. Responsive Behavior

| Breakpoint | Screen Size | Sidebar Behavior | Chat Area | Artifact Viewer |
|---|---|---|---|---|
| **Desktop** | $\ge 1200\text{px}$ | Fixed 260px left sidebar | Centered or 50% width | 50% split pane beside chat |
| **Tablet** | $768\text{px} - 1199\text{px}$ | Collapsible drawer (hamburger toggle) | Full width | Slides over chat as a 70% width right drawer overlay |
| **Mobile** | $< 768\text{px}$ | Hidden bottom navigation / drawer | Full width (100vw) | Full-screen modal with fixed top close header |

---

## 6. Accessibility (a11y)

The frontend strictly adheres to WCAG 2.1 AA accessibility guidelines:

- **Keyboard Navigation:**
  - Full keyboard control across all interactive elements (`Tab` and `Shift + Tab`).
  - `Ctrl + N` / `Cmd + N`: Create new chat.
  - `Ctrl + /` / `Cmd + /`: Focus message composer.
  - `Escape`: Close active Artifact Viewer or model popover.
- **ARIA & Assistive Tech:**
  - Accessible names (`aria-label`) on all icon-only buttons (send, copy, close, expand).
  - Live regions (`aria-live="polite"`) for streaming assistant responses to announce new content to screen readers.
- **Focus Management:**
  - When the Artifact Viewer opens, keyboard focus moves automatically to the viewer header close button or title.
  - Closing the viewer restores focus to the triggering "Open in Viewer" button in the chat thread.
- **Color Contrast:**
  - All text and interactive controls maintain a contrast ratio of $\ge 4.5:1$ against their backgrounds in both dark and light modes.
- **Reduced Motion:**
  - CSS media query `@media (prefers-reduced-motion: reduce)` disables smooth scrolling and animations for users with vestibular sensitivities.

---

## 7. Design Decisions and Trade-offs

### 1. Split Pane Instead of Tabs for Artifacts
- **Decision:** Render artifacts in a dedicated side-by-side split pane rather than tabbed navigation within the chat bubble.
- **Rationale:** A growth PM analyzing an essay draft, onboarding checklist, or metrics wireframe needs to reference the conversational context (prompts, suggestions, and source citations) simultaneously. Switching between tabs creates cognitive friction and breaks workflow continuity.

### 2. Citation Chips Instead of Inline Footnotes
- **Decision:** Place distinct, interactive citation chips at the bottom of each answer rather than tiny numeric footnotes within the text.
- **Rationale:** Inline superscripts like `[1]` disrupt reading rhythm and often feel like academic papers. Visual citation chips emphasize provenance as a tangible deliverable, highlighting the guest and episode while making source verification a one-click action.

### 3. Streaming Responses Instead of Blocking
- **Decision:** Stream tokens via Server-Sent Events (SSE) rather than waiting for full completion.
- **Rationale:** Local 8B LLM inference on consumer hardware can require 4–8 seconds to generate complete responses, and up to 15 seconds for ~1,250-word Ship 30 essays. Token streaming provides instantaneous feedback within 500ms, reassuring the user that the system is actively generating output.
