# Selected prompts — Assignment 3.2

This curated record excludes credentials, personal information, real distress disclosures, and full chat history.

## End-to-end skill scope

> Implement one selected skill through Vue, FastAPI, and SQLite. Keep the canonical 4-in/6-out breathing sequence intact, measure active practice from first instruction through final cycle, keep exits consequence-free, and do not claim that deferred skills are available.

**Decision:** Implement paced breathing only, six cycles / 60 active seconds. Keep grounding documented as deferred.

## Independent safety route

> Keep a clearly labelled support route present in the browser through every state and after a model/API failure. It must not depend on a classifier, prompt, or network call.

**Decision:** Render the dialog in Vue and use a dedicated local-safety lookup to verify the current U.S. support links before including them.

## Bounded companion

> Permit the model only after a completed practice and only for an optional fictional note. Backend validation—not a system prompt alone—must reject advice, diagnosis, model-directed skill changes, and unsafe output. Potential-crisis text must not be stored or transmitted.

**Decision:** Use a backend-only OpenRouter client, a narrow local phrase route, output limits/terms, and a fixed fallback.

## Browser proxy revision

> When the browser can load the Vue dev server but cannot reach a separate localhost API directly, keep the API boundary intact and make development requests same-origin through Vite’s `/api` proxy.

**Decision:** Added an environment-configurable Vite proxy. Production build remains dependency-free.

## Navigation and session integrity revision

> If someone leaves an active practice by choosing a top-level navigation action, preserve their control without leaving an unfinished active session in the local history.

**Decision:** Before opening Saved history or returning home, Vue finishes the active session as a neutral `stopped` record. If that save fails, it stays on the current screen and shows the error instead of pretending the exit was saved.

## History review clarity

> Make the saved-history view useful for fictional evaluation without turning it into a score or asking for more disclosure.

**Decision:** Each session card shows the active seconds and whether it was directly chosen or an optional repeat, alongside its neutral outcome and date. Optional notes and companion replies remain in a separate list.

## Optional profile and bounded chatbot revision

> Add a demonstrable user profile without collecting emotional, health, or inferred-state data. Make every profile setting optional, editable, and resettable. Let the interface and a bounded post-practice chatbot use only explicit profile choices and neutral usage history; do not change a canonical skill step.

**Decision:** Store only an optional display name, cue-style selection, and practice-aim selection in local SQLite. The home screen adapts its greeting and cue explanation; the latest completed skill remains an optional repeat shortcut. The backend chatbot receives those explicit choices and a completed-practice count only after a completed skill, while the frontend labels its scope and limitations clearly.

## Deterministic chatbot example

> Add one presentation-ready response for the exact fictional phrase `I am tired`, while preserving the coursework chatbot's non-directive, non-medical limits.

**Decision:** Handle the exact phrase locally before a model request with “Thanks for the fictional note. Rest may be one choice to consider; you can choose what happens next.” Do not prescribe a sleep duration or imply health guidance.
