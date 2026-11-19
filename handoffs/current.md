# Current handoff — Assignment 4.2

Continue the Vue/FastAPI/SQLite market workstation on `codex/assignment4-2`. Part 4.1’s submitted report is preserved at `reports/assignment4-part1/report.md`, with its published branch and evidence intact. `/stillpoint` preserves the former skill app and its data/safety boundaries.

Part 4.2 adds closed-only SMA(5)/SMA(20), provisional chart previews, optional forward paper accounts, immutable historical Yahoo snapshots and sequential next-open backtests. Simulated ledger uses Decimal, entry/exit fees, adverse slippage, fractional units and full long-only positions. Results include durable orders/fills, cash, position, realized/unrealized P/L, equity, return and completed-bar drawdown. No broker or Part 4.3 AI/audio exists.

No new dependencies were needed. Existing pandas provides a trusted independent rolling-window test reference. Genuine Yahoo AAPL sample: 161 hourly bars, hash `44e37cd3c962fa3baec80b76b5460a86be9dd819960fa5817843ff0878b0fc7c`. Default run: 9 fills, 4 completed exits, 27.294663 units remaining, $9,615.64 equity, −3.84% return; the loss is preserved without tuning.

Read README, design and `docs/assignment4-part2-verification.md` for exact startup, bias/accounting assumptions and evidence. `.github/workflows/checks.yml` runs backend tests, frontend indicator tests, production build and a Chrome browser regression on every push/PR using recorded source data with live feed disabled. The first actual run passed; final run/link is recorded in the verification document.

Before submission, stop any optional demo paper account, verify final public repository/video URLs, and upload only root `report.md` to Canvas. Leave the two pre-existing Assignment 1 screenshot deletions unstaged. Credentials stay solely in ignored root `.env`; generated DB and yfinance caches are ignored. Further updates must preserve event-time causality and never rewrite prior paper fills using revised historical candles.
