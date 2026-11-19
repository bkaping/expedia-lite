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
| 2026-11-02 | Selected model-summary revision | Replaced the removed free-text path with one explicit fixed summary button after completion. The fake-model tests confirm allowed context, persistence, completion gating, failure fallback, and unsafe-output fallback. |
| 2026-11-02 | Limited live-model comparison | Two fixed no-profile fictional 60-second summary prompts returned factual outputs from `dots-studio/dots-3-note-preview:free` and `nvidia/nemotron-3.5-lightning:free`. A profile-bearing live check was not run to avoid exporting local profile data. |

This is a redacted record. It contains no credential, real distress content, participant information, or full chat transcript.

## Assignment 4.1 — November 19, 2026

| Intended change / instruction | Resulting code or artifact | Check / decision / uncertainty |
|---|---|---|
| “Just do 4.1”; preserve previous coursework | `frontend/src/market.js`, `stillpoint.js`, `backend/app/market/` | Separate default dashboard and `/stillpoint`; no Part 4.2/4.3 features. |
| CHECK → approval → install dependencies | yfinance 1.8.0, lightweight-charts 5.3.0; requirements and npm lock | Missing packages checked; student approved both; Python sandbox network restriction required permitted network retry. |
| Connect actual Yahoo stream | `feed.py` certifi CA configuration | Initial Python default-CA handshake failed. Trusted bundle fixed it with TLS checking enabled. This is the selected failed/revised approach. |
| Preserve duplicates, revisions, late events and completion | `store.py`, `test_market.py` | 11 deterministic market cases; 33 total tests pass. Timestamp-based identity cannot recover Yahoo's absent exchange trade IDs. |
| Demonstrate live → backend → DB → chart; retain data when unavailable | `scripts/verify_market_live.py`, `assignment4-evidence/live-verification.json`, browser PNGs | Real Yahoo candle equals SQLite by event ID; source age visible; deliberate disconnect retains candles; fixed-boundary replay equals DB. No synthetic source data used in these checks. |

See [the focused verification record](assignment4-verification.md) for recording, reproducibility, and submission limitations. Public market payloads only; no `.env`, credentials, old profile/journal records, private communications, or full chat export.

Final checks also exposed SQLite handles that the Python connection transaction context did not close. `MarketStore.connect()` now explicitly closes them in `finally`; the focused market suite passed with ResourceWarning enabled. Browser reconnection was adjusted to retain saved candles during a backend outage and verified by stopping/restarting FastAPI. Final-source replay/DB checks and a clean Git archive test/build passed; see the verification record.

## Assignment 4.2 — November 19, 2026

| Question / instruction | Generated result | Evidence / decision / remaining limit |
|---|---|---|
| Add two SMAs and crossovers; verify a trusted reference | `strategy.py`, `indicators.js`, indicator tests | Published 3-period values and pandas rolling/vectorized crosses agree; independent batch and incremental calculations match on 1,200 seeded observations. Unfinished values remain previews. |
| Apply crossover to a simulated account and check accounting | Decimal `Ledger`, `Simulation`; known-account tests | $1,000 → 9.99 units → $1,197.80 net cash example verified, including both $1 fees. Source receipts and fills remain separate. |
| Backtest without future information | `simulation.py`, immutable datasets/runs; causality tests | Each next-open fill follows an earlier close; future mutations cannot alter prior equity/signals. Real AAPL run retained its −3.84% loss rather than tuning windows. |
| Revised approach: historical opens can be stale in a forward account | `Simulation.next_open`, paper event processor | Live path now uses the first eligible later received quote; pre-signal receipts are rejected and older corrections never rewrite fills. Synthetic zero-low fixture and test-clock mistakes were corrected after failed tests, preserving strict validation. |
| Keep browser tests and checks on pushes | `.github/workflows/checks.yml`, `scripts/browser_smoke.py` | Actual GitHub run 44548261750 passed backend/frontend/build/browser checks on push. CI explicitly loads recorded Yahoo data with live source disabled; it is not evidence of a new Yahoo connection. |
| Trace actual source data into stored runs and visible results | Yahoo sample, API verification, browser screenshots, 40s video | 161 real hourly bars; pandas max SMA error 5.68e-14; saved run reopens identically; account/fill history and equity shown. No new paper crossover occurred during the live clip. |

[Part 4.2 verification](assignment4-part2-verification.md) records exact results, process revision, CI and limitations. No credential, private profile/journal, real account, private third-party content or full chat export is included.
