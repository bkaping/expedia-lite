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
