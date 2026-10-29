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
| 2026-10-29 | Complete configured browser flow | A fictional session completed at 60 active seconds, received the bounded reply “Noted. You completed the fictional practice. You can choose what to do next.”, and displayed the session, note, and reply in history. |
| 2026-10-29 | Profile/chatbot implementation checks | 17 backend tests passed and the Vue production build passed after adding the optional local profile, reset path, and explicit profile/history chatbot context. An isolated browser check saved fictional profile `Avery`, then visibly changed the home greeting, cue explanation, and aim. |
| 2026-10-29 | Persistent chatbot UI check | Isolated browser check confirmed the top-right Coursework chatbot control opened its bounded, non-therapeutic panel and honestly required a completed fictional practice before sending a message. |
| 2026-10-29 | Scripted tired-message check | Added a local response for exact fictional `I am tired`; automated test confirmed it returns the non-directive script and makes zero model calls. The full backend suite now has 18 passing tests. |
| 2026-10-29 | Local journal check | Added two focused journal tests and rechecked the full 20-test suite plus production build. In an isolated browser check, a fictional entry saved locally and appeared immediately in the Journal list. |
| 2026-10-29 | Common-question chatbot check | Added local factual answers and visible prompt buttons for common website questions. A focused test confirmed the journal-separation answer makes zero model calls; the full suite now has 21 passing tests and the production build passed. |
| 2026-10-29 | Fixed chatbot and pacing-control revision | Replaced the free-text/model companion with seven local factual questions and removed chatbot-message persistence. Added automatic and tap-and-hold controls for the same fixed 4-in / 6-out skill. The revised backend suite has 18 passing tests and the Vue production build passed. |
| 2026-10-29 | Isolated browser controls check | The local factual chatbot showed all seven questions and returned the no-profile/no-history setup answer. A 1.2-second tap-and-hold advanced the timer from 60 to 59 seconds; release paused it, and ending saved a neutral stopped record with 1 active second. |

This is a redacted record. It contains no credential, real distress content, participant information, or full chat transcript.
