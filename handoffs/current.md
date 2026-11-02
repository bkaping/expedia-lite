# Current handoff — Stillpoint Assignment 3

## What works

- Vue implements one paced-breathing flow: preparation, six 4–6 cycles, automatic visual timing or tap-and-hold pacing, neutral leave route, and finish state.
- FastAPI initializes ignored SQLite `backend/data/skills_practice.db` and persists sessions, profiles, journal entries, and selected fixed model-summary exchanges.
- The history screen shows recent sessions plus selected model-summary records. A completed breathing session becomes an optional repeat shortcut.
- The browser-local Crisis support control is present across home, practice, finish, and history states; it does not call FastAPI or the model.
- A persistent Coursework chatbot control appears beside Crisis support. It offers seven fixed factual questions and one optional post-completion model-summary prompt; it accepts no free-text message. The model receives only timing, cue/aim choices, and completed-practice count; only the selected prompt/reply is stored.
- The optional Journal page stores 500-character fictional entries separately and never sends them to a model. It has the same limited no-store potential-crisis route.
- An optional local profile stores only a display name, cue style, and practice aim. The saved choices change the greeting/cue explanation and can be summarized by a fixed chatbot answer or the bounded model-summary prompt with neutral completed-practice count.
- Vite proxies `/api` in development; set `VITE_API_PROXY_TARGET` only when using a non-default backend port.

## Checked on October 15, October 29, and November 2, 2026

- Backend suite: 22 passing tests, including optional-profile persistence/reset, fixed chatbot answers, allowed model context, model failure/unsafe-output fallback, and journal save/safety handling.
- Frontend production build: passed.
- Browser: static support panel, pre-start voluntary exit → `stopped`/0 seconds, history rendering, full 60-second completion, active-practice navigation → neutral stopped history record, and a saved/displayed local fictional journal entry. The current check also confirmed all chatbot prompts, a 1.2-second tap-and-hold advance followed by a neutral 1-second stopped record, and persisted selected model summaries.
- Live model: two fixed, no-profile fictional summary calls returned factual outputs from two provider-selected free models; model variation is logged in `docs/assignment3-evaluation.md`.

## Remaining for Part 3.3

1. Capture the required finished-demo and failure-investigation recordings using `docs/assignment3-recording-plan.md`.
2. Test reduced motion, keyboard-only tap-and-hold flow, and a fuller range of interruption/failure cases with another reviewer.
3. Add the recording links and final submitted commit hash to the Part 2/Part 3 reports without exposing credentials.
