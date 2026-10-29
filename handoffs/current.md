# Current handoff — Stillpoint Assignment 3

## What works

- Vue implements one paced-breathing flow: preparation, six 4–6 cycles, pause, neutral leave route, and finish state.
- FastAPI initializes ignored SQLite `backend/data/skills_practice.db` and persists session and optional conversation records.
- The history screen shows recent sessions/messages. A completed breathing session becomes an optional repeat shortcut.
- The browser-local Crisis support control is present across home, practice, finish, and history states; it does not call FastAPI or the model.
- A persistent Coursework chatbot control appears beside Crisis support. It explains its limits before completion, then accepts fictional messages after a completed practice; it has backend-only output validation/fallback and redacts limited potential-crisis input before a model call.
- Exact fictional message `I am tired` is a tested local scripted response, so no model call is made; it remains non-directive and avoids sleep/medical recommendations.
- An optional local profile stores only a display name, cue style, and practice aim. The saved choices change the greeting/cue explanation, are editable/resettable, and are sent to the bounded chatbot only with a neutral completed-practice count.
- Vite proxies `/api` in development; set `VITE_API_PROXY_TARGET` only when using a non-default backend port.

## Checked on October 15 and rechecked on October 29, 2026

- Backend suite: 18 passing tests, including optional-profile persistence/reset, chatbot-context boundaries, and the local scripted tired-message response.
- Frontend production build: passed.
- Browser: static support panel, pre-start voluntary exit → `stopped`/0 seconds, history rendering, full 60-second completion, fictional-note model acknowledgment, and active-practice navigation → neutral stopped history record. The October 29 complete flow showed the session’s active time/source and both fictional note/reply in history.
- Key-disabled localhost companion API: HTTP 503 `companion_not_configured` without another model call.

## Remaining for Part 3.3

1. Complete the required 15 fictional scenarios and three explicit cross-case checks, using mocked responses by default.
2. Capture the required finished-demo and failure-investigation recordings, including a profile save/reset and bounded chatbot response.
3. Test reduced motion, keyboard-only flow, and a fuller range of interruption/failure cases.
4. Update `AI-USE.md`, evidence log, and the report with later tests/recordings without exposing credentials.
