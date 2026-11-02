# Stillpoint — Assignment 3.2 working application

## Submission checkpoint

- Repository: `https://github.com/bkaping/expedia-lite`
- Implementation checkpoint: **replace with the verified Part 3.2 commit hash before upload**
- Run instructions: [README](../../README.md)
- Design and safety decisions: [design note](../../docs/design.md)
- Verification: [verification record](../../docs/assignment3-verification.md)

## What works

Stillpoint implements the study-provided paced-breathing skill: six cycles of four-second inhale and six-second exhale, measured as 60 active seconds. A person may choose automatic visual timing or tap-and-hold pacing; both preserve the same canonical sequence. Pause/end controls are consequence-free, and stopped sessions are saved as neutral records.

Vue owns the skill flow, pacing cue, exits, history presentation, and persistent browser-local Crisis support panel. FastAPI owns SQLite and the model call. SQLite stores sessions, the optional explicit profile, optional fictional journal entries, and only a selected fixed model-summary exchange. The app never sends journal text or an LLM key to the browser or model provider.

The chatbot uses fixed buttons rather than a disclosure textbox. Website questions are local and deterministic. After a completed fictional practice, one fixed “Create a brief practice summary” prompt may use the backend model with only session timing, optional cue/aim choices, and completed-practice count. It never sends a display name or journal text. The app validates the output and uses a local fallback after unavailable, failed, or unsafe model output.

## Screenshot evidence

Use these four captures with the report upload:

1. **Home screen:** coursework boundary, optional profile entry, and optional repeat shortcut.
2. **Pacing-control screen:** automatic visual timing and tap-and-hold pacing for the unchanged 4-in / 6-out sequence.
3. **Chatbot screen:** fixed factual questions plus the single fixed optional model-summary prompt; no free-text message field.
4. **Saved history:** completed/stopped sessions and selected model-summary records.

## Evidence and remaining work

Backend checks cover persistence, neutral stops, profile edit/reset, local chatbot facts, fixed model-summary context, model failure, unsafe output, journal separation, and the journal phrase route. The frontend production build passes. The support route is browser-local and stays available if FastAPI or the model request fails.

The later Part 3.3 package adds the 15 fictional scenarios, cross-case behavior checks, mocked/live comparison, surprising finding, limitation, and recording plan in [the Part 3 evaluation](../../docs/assignment3-evaluation.md). This prototype is not a clinical tool and does not establish clinical usefulness.
