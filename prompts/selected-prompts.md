# Selected prompts — Assignment 3.2

This curated record excludes credentials, personal information, real distress disclosures, and full chat history.

## End-to-end skill scope

> Implement one selected skill through Vue, FastAPI, and SQLite. Keep the canonical 4-in/6-out breathing sequence intact, measure active practice from first instruction through final cycle, keep exits consequence-free, and do not claim that deferred skills are available.

**Decision:** Implement paced breathing only, six cycles / 60 active seconds. Keep grounding documented as deferred.

## Independent safety route

> Keep a clearly labelled support route present in the browser through every state and after a model/API failure. It must not depend on a classifier, prompt, or network call.

**Decision:** Render the dialog in Vue and use a dedicated local-safety lookup to verify the current U.S. support links before including them.

## Fixed questions and selected model summary

> Replace free-text chatbot messages with reliable factual questions, while retaining one deliberate model contribution that can be evaluated and reviewed.

**Decision:** Provide seven visible question buttons backed by local scripts plus one post-completion “Create a brief practice summary” button. The panel accepts no free text. Only the selected summary prompt/reply is persisted; its backend model context is session timing, explicit profile choices, and completed-practice count—not journal text or a disclosure.

## Browser proxy revision

> When the browser can load the Vue dev server but cannot reach a separate localhost API directly, keep the API boundary intact and make development requests same-origin through Vite’s `/api` proxy.

**Decision:** Added an environment-configurable Vite proxy. Production build remains dependency-free.

## Navigation and session integrity revision

> If someone leaves an active practice by choosing a top-level navigation action, preserve their control without leaving an unfinished active session in the local history.

**Decision:** Before opening Saved history or returning home, Vue finishes the active session as a neutral `stopped` record. If that save fails, it stays on the current screen and shows the error instead of pretending the exit was saved.

## History review clarity

> Make the saved-history view useful for fictional evaluation without turning it into a score or asking for more disclosure.

**Decision:** Each session card shows the active seconds and whether it was directly chosen or an optional repeat, alongside its neutral outcome and date. History separately shows only selected fixed model-summary prompt/reply pairs, not local FAQ taps or free-text content.

## Optional profile and factual chatbot revision

> Add a demonstrable user profile without collecting emotional, health, or inferred-state data. Make every profile setting optional, editable, and resettable. Let the interface and a factual chatbot use only explicit profile choices and neutral usage history; do not change a canonical skill step.

**Decision:** Store only an optional display name, cue-style selection, and practice-aim selection in local SQLite. The home screen adapts its greeting and cue explanation; the latest completed skill remains an optional repeat shortcut. The factual chatbot’s saved-setup question and selected model summary use only those explicit choices and the completed-practice count.

## Pacing-control revision

> Provide automatic and tap-and-hold ways to control pacing without adding or changing a canonical breathing exercise.

**Decision:** Keep one 60-second 4-in / 6-out skill. Automatic mode advances the cue; tap-and-hold counts only while the control is held and pauses on release. Each phase still ends at four or six active seconds, so the interaction mode cannot replace or reorder the canonical steps.

## Local fictional journal

> Add an optional journal that persists explicit fictional entries without expanding what the model receives or requiring an emotional disclosure.

**Decision:** Add a separate SQLite journal table and a Vue Journal page. Store only the voluntarily entered body and timestamp, show the latest 12 entries, never send journal text to the model, and do not save limited potentially urgent wording.

## Common chatbot questions

> Add reliable common questions about the website without needing the language model to invent factual details.

**Decision:** Add visible question buttons in the chatbot and map their exact prompts to local scripted answers. The factual answers cover scope, breathing timing, stopping, saved data, journal separation, profile behavior, and the saved setup; they do not call a model. A visibly distinct fixed summary button is the sole model path and its exchange is retained for review.

## Assignment 4.1 — November 19, 2026

User scope: “Just do 4.1.” Requirements: “Connect to Yahoo Finance … updating candlesticks and corresponding volume … WebSockets … preserve observation identity, source and receipt times, revisions, and whether a candle is complete.”

Student approved both proposed dependencies after checking the existing environment: yfinance for the source stream and Lightweight Charts for charting. Implemented only the dashboard/persistence/replay portion, retaining the former app separately. Relevant generated code: `backend/app/market/store.py`, `feed.py`, `routes.py`, `frontend/src/market.js`, and `backend/tests/test_market.py`.

Revised approach: real-source verification initially failed with `SSLCertVerificationError`; supplying the already-installed certifi CA bundle fixed the handshake while keeping certificate checks. Deterministic test cases cover revision, duplicate and late-arrival behavior; `scripts/verify_market_live.py` verifies actual source/socket/database equality, saved data during disconnection, and replay at a fixed boundary. See [evidence](../docs/assignment4-verification.md). No AI market decision is implemented or claimed.

## Assignment 4.2 — November 19, 2026

User scope: “Indicators, Simulated Trading, and Backtesting”; “Verify the moving averages and crossover against a trusted reference, compare batch and incremental calculations … Check simulated accounting against known examples … automated checks on pushes using GitHub Actions.”

Decision: retain Part 4.1 source/revision/replay behavior; add closed-only SMA(5)/SMA(20), explicit provisional previews, forward paper accounts, immutable Yahoo hourly snapshots, and sequential next-open backtests. Existing pandas/yfinance/chart dependencies were sufficient; no dependency install or subagent was used. Generated code: `market/strategy.py`, `simulation.py`, `strategy_routes.py`, Vue `strategy-panel.js`, `test_strategy.py`, and the GitHub workflow/browser regression.

Revised approach: historical “next open” fills cannot be reused blindly for forward paper trading because the old open may already have occurred when a signal becomes known. Forward fills instead use the first eligible next-interval received quote. Tests verify that a pre-signal receipt cannot fill and that the actual later quote, rather than the interval’s older open, sets the price. A malformed synthetic OHLC fixture initially had a zero low and correctly failed dataset validation; the fixture was repaired without weakening validation. Test clock timing was also corrected so a late-revision check did not accidentally advance a different candle to completion.

Evidence: pandas/batch/incremental comparisons, Decimal known-account example, future-prefix invariance, durable restart/idempotence, saved Yahoo run/API equality, and the actual GitHub Actions browser run. See [Part 4.2 verification](../docs/assignment4-part2-verification.md). Historical loss was retained; no parameter search or profitable-outcome claim was added.
