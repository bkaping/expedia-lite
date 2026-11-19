# Current handoff — Assignment 4.1

Market workstation is the default Vue page; Assignment 3 remains at `/stillpoint`. FastAPI starts one Yahoo WebSocket subscription and a candle-finalization task. Market records use ignored `backend/data/market.db`, isolated from prior coursework. See [README](../README.md), [schema and tradeoffs](../docs/design.md), and [verification](../docs/assignment4-verification.md).

Student approved adding yfinance 1.8.0 and Lightweight Charts 5.3.0 on November 19, 2026. Existing certifi resolves missing macOS Python default CA certificates without disabling TLS checks. No market credentials or new LLM calls.

Completed checks: 33 backend tests and production build; actual Yahoo → SQLite → browser WebSocket equality; failure retention and bounded replay equality. Unit scenarios are artificial fixtures; live evidence uses genuine public Yahoo observations. Keep those claims distinct.

Submission is only root `report.md`. Final repository/video accessibility must be verified for the instructor. Do not claim an upload or accessible remote video until it exists. Preserve the two already-deleted Assignment 1 screenshots as unrelated working-tree changes. Part 4.2/4.3 indicators, accounts, AI, and audio are outside this task.
