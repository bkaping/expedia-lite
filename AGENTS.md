# Stillpoint project guidance

- Keep the Vue client in `frontend/` and the FastAPI service in `backend/`. Vue owns the skill flow, pacing cue, exits, visible history, and static crisis panel. FastAPI owns SQLite and all optional LLM calls. The browser must never receive an LLM key.
- This is a coursework prototype for fictional scenarios only. Never describe it as therapy, diagnosis, monitoring, crisis care, or something a person should rely on while distressed.
- Keep the canonical skill steps intact. Part 3.2 implements paced breathing (inhale 4 / exhale 6); 5–4–3–2–1 grounding remains documented as planned. Do not let generated output add, reorder, or replace a skill step.
- Keep crisis support persistently visible and functional in the browser even if FastAPI or the LLM fails. Any input screening is limited, documented, and must never be represented as a distress detector.
- Minimize emotional and data cost: do not require a disclosure to finish a skill. Store only the documented session fields and explicit optional fictional notes. Do not store or transmit detected potential-crisis content.
- Personalization may offer the latest completed skill as a shortcut but must not auto-route someone, hide the other choices, or require a preferences setup flow.
- Store credentials only in root `.env`; keep it ignored and commit only `.env.example`. Keep generated SQLite databases ignored.
- Follow CHECK → TAKE ACTION → VERIFY before adding a dependency: inspect the existing environment, explain the exact installation and wait for student approval, then install and verify with focused checks and a build.
- Preserve keyboard usability and the `prefers-reduced-motion` alternative for the visual breathing cue.
- Run backend unit tests and a frontend production build before committing functional changes.
- Keep `README.md`, `docs/design.md`, `docs/assignment3-verification.md`, `prompts/selected-prompts.md`, and `handoffs/current.md` concise and current when the application changes.

## Assignment 4.1 market workstation

- The default Vue entry is the market dashboard (`market.js`); preserve the previous Stillpoint UI at `/stillpoint` (`stillpoint.js`) and apply the guidance above to that archived application.
- Scope this part to Yahoo Finance streaming, candlesticks/observed volume, SQLite persistence, replay, and honest evidence. Do not add indicators, trading, AI decisions, or audio for Part 4.1.
- Backend owns the single Yahoo WebSocket connection, source/receipt timestamps, identity/revisions, atomic raw/receipt/candle writes, completion, and fixed-boundary replay. Browser receives only committed market records through FastAPI WebSockets; enable Vite `ws: true`.
- Document timestamp-derived identity ambiguity, observed-volume limitations, late corrections, and closed-interval vs complete market coverage. Never present generated fixtures, recorded data, or a refreshed socket as proof of current live data.
- Market SQLite initializes automatically; ignore DB/WAL files. No Yahoo credentials required. Keep any credentials in root `.env`; never disable TLS verification.
- Keep `report.md`, `docs/assignment4-verification.md`, `docs/design.md`, README, AI-USE, selected prompts, evidence log and handoff current. Capture genuine live-source and unavailable-feed evidence; distinguish those checks from deterministic fixtures.

## Assignment 4.2 extension

- Continue the published Part 4.1 workstation; its report/evidence stay archived. Part 4.2 adds SMA(5)/SMA(20), forward paper accounts and immutable historical backtests. All trades remain simulated. Part 4.3 AI/audio is outside scope.
- Confirmed indicators consume only closed candles. Unfinished values/crossovers are previews and never submit orders. Backtests decide after close and fill only at a later bar open; forward paper orders use a later received quote, never an already-known historical open.
- Keep historical dataset identity/source/fetch time and run parameters/results immutable in SQLite. Keep paper event cursors and order/fill history durable; duplicates and late closed-bar corrections must not replay trades.
- Use Decimal for simulated cash/cost basis/fees. Test accounting identities, known examples, next-bar causality, prefix invariance, unfinished candles, pandas reference agreement and incremental/batch agreement.
- Run `.github/workflows/checks.yml` on pushes: backend and frontend indicator tests, production build, and browser regression against the explicitly included real Yahoo historical snapshot. CI never depends on a live market.
- Keep `docs/assignment4-part2-verification.md`, report, design, README, handoff, AI disclosure and curated evidence current. Explain look-ahead, survivorship and overfitting limits. Preserve all earlier coursework boundaries.
