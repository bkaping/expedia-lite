# Assignment 3 evidence log

| Date | Evidence | Decision / result |
| --- | --- | --- |
| 2026-10-15 | Part 3.1 design and assignment findings | Selected paced breathing as the one Part 3.2 skill and deferred grounding rather than claiming a broad untested library. |
| 2026-10-15 | Focused fake-model tests | Added session persistence, bounded response, redaction-before-model, and unsafe-output fallback coverage. 16 total backend tests passed. |
| 2026-10-15 | Production frontend build | `npm run build` passed. |
| 2026-10-15 | Browser with real SQLite API | Observed static crisis panel, voluntary pre-start exit (`stopped`, 0 seconds), saved history, and 60-second completion. |
| 2026-10-15 | One live-model fictional note | Model returned `Acknowledged.` for a fictional note. This is one observed variation, not proof of consistency or usefulness. |
| 2026-10-15 | Key-disabled local API | `POST /api/conversations` returned HTTP 503 `companion_not_configured` without a model call. Kept the static panel browser-local. |
| 2026-10-15 | Browser connectivity issue | Direct browser-to-separate-localhost API requests failed in the verification environment. Added Vite’s same-origin `/api` development proxy rather than weakening API boundaries. |
| 2026-10-29 | Current checkout test/build recheck | All 16 backend tests and the frontend production build passed. |
| 2026-10-29 | Browser navigation check | Navigating from an active practice to Saved history now records a neutral stopped session before the history screen opens. This closed an active-session edge case. |
| 2026-10-29 | SQLite inspection | Queried only session metadata, not note text. The newest record was a `usual_skill` paced-breathing session with `stopped` outcome and 0 active seconds, matching the browser navigation check. |
| 2026-10-29 | Key-disabled local API recheck | A completed temporary session received HTTP 503 `companion_not_configured` at the companion endpoint, without a provider call. |

This is a redacted record. It contains no credential, real distress content, participant information, or full chat transcript.
