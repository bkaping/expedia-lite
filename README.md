# Market workstation — Assignment 4.2

Local Vue + FastAPI + SQLite dashboard for Yahoo Finance streaming observations. **Part 4.2:** SMA(5)/SMA(20) overlays and crossovers, optional forward paper accounts, and historical backtests with persisted simulated orders, fills, cash, positions and P/L. Part 4.1 live streaming, source age, revisions and replay remain intact. All trading is simulated; no broker, AI market decisions or audio is connected.

## Start from a clean checkout

Python 3.11+ and Node 20+ are required. Dependency installation was approved by the student on November 19, 2026; follow `AGENTS.md` before adding anything else.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open [localhost:5173](http://127.0.0.1:5173). Vite proxies HTTP **and WebSockets** under `/api` to port 8000. SQLite initializes automatically at `backend/data/market.db` (WAL, schema version 2); no manual SQL or Yahoo credential is required. Optional settings go in ignored root `.env`, using `.env.example`. No browser receives credentials. Bind to loopback only: feed controls are intended for a single trusted local user.

Choose AAPL, MSFT, or BTC-USD. Yahoo subscribes once in the backend, independently of browser tabs. The chart starts with real received observations; it does not invent historical candles. Stocks may be quiet outside market hours. Source age is measured from Yahoo's timestamp, separately from receipt time and browser connectivity. “Live” requires a source age and recent receipt within 30 seconds. Closed means the minute elapsed, not that every exchange trade was observed. Volume is an **observed change in Yahoo's cumulative counter**, with unknown/reset handling; crypto's rolling counter is not exchange trade volume. See [design limitations](docs/design.md).

## Indicators, simulated account, and historical backtest

- The chart overlays short/long SMAs and marks BUY/SELL crossovers. Default windows are 5/20 observed bars; configurable from 2 to 100 with short < long. Only closed candles advance the confirmed indicator state. The unfinished candle is a visible provisional preview and cannot place an order.
- **Live feed → Start paper strategy** creates a $10,000 simulated account by default. Closed history warms up the SMAs without placing historical orders. Subsequent confirmed crossovers queue orders; the first eligible later received quote fills them. Stop cancels a pending order and leaves any position marked at its last processed quote. One active account per symbol; accounts and event cursors survive restart.
- **Historical backtest → Load included AAPL snapshot → Run backtest** works without Yahoo availability. The included genuine Yahoo snapshot has 161 completed hourly bars and an immutable content hash. **Fetch Yahoo history** explicitly captures another month of hourly regular-session OHLCV; failed fetches show an error without substituting a different dataset.
- Backtests decide at close and fill at the next available bar open, using only the processed prefix. Defaults: long only, all affordable cash, fractional units truncated to six decimals, $1 per fill, five basis points adverse slippage, no leverage/dividends/interest. Entry fees belong to cost basis; realized P/L uses net exit proceeds; remaining positions are marked at the last close without forced liquidation.
- Run results include equity, cash, units, realized/unrealized P/L, returns, maximum close-to-close drawdown, orders and fills. Saved datasets and runs can be reopened. Historical results do not establish future performance; unadjusted bars and missing observations limit interpretation. [Design and formulas](docs/design.md) explain the exact assumptions and bias risks.

## Persistence, offline replay, and failure demo

- **Recorded replay** plays saved candle revisions at 10 events/sec through a fixed database event boundary. It starts empty, preserves arrival order, and never inserts replay data into the live database. This is observation replay, not backtesting.
- **Disconnect feed · failure demo** closes the Yahoo connection while retaining SQLite records and the browser connection. Use **Reconnect Yahoo feed** to resume.
- To exercise recorded real Yahoo data on an offline checkout, import the included public recording into a new database before starting FastAPI:

```bash
.venv/bin/python scripts/market_recording.py import backend/data/replay.db docs/assignment4-evidence/yahoo-observations.jsonl
MARKET_DB_PATH=backend/data/replay.db MARKET_FEED_ENABLED=0 .venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Choose BTC-USD and Recorded replay. Recorded data is never proof of a new live connection. Export a fresh recording with `scripts/market_recording.py export backend/data/market.db /tmp/yahoo-observations.jsonl`. Databases are ignored; the curated JSONL contains public market observations only. A fresh database has no candles until a live receipt or explicit recording import.

## Verify

```bash
.venv/bin/python -m unittest discover -s backend/tests -v
node --test frontend/src/indicators.test.js
npm --prefix frontend run build
# With the backend running and fresh BTC-USD observations available:
.venv/bin/python scripts/verify_market_live.py
```

[Part 4.2 verification and evidence](docs/assignment4-part2-verification.md) distinguish deterministic fixtures from real-provider checks. The [GitHub Actions workflow](.github/workflows/checks.yml) runs all backend tests, frontend indicator tests, a production build and [Chrome browser regression](scripts/browser_smoke.py) on every push/PR. It uses the runner’s preinstalled ChromeDriver and the included recorded Yahoo sample; CI has the live feed disabled. No new dependencies were added for Part 4.2.

Run `.venv/bin/python scripts/verify_strategy.py` with FastAPI running to compare a saved Yahoo backtest with pandas and verify persisted account results. [Part 4.1 report](reports/assignment4-part1/report.md) and [evidence](docs/assignment4-verification.md) remain archived. [Schema/design](docs/design.md), [submission report](report.md), [AI disclosure](AI-USE.md), [selected prompts](prompts/selected-prompts.md), and [handoff](handoffs/current.md) explain the implementation.

The existing Assignment 3 Stillpoint prototype remains at `/stillpoint`; its canonical skill, browser-local support panel, and data boundaries are preserved. See the [archived README](docs/assignment3-readme.md) and [verification](docs/assignment3-verification.md).

Chart library: [TradingView Lightweight Charts](https://tradingview.github.io/lightweight-charts/docs), Apache 2.0. Copyright (с) 2025 TradingView, Inc. Chart attribution and a TradingView link are visible in the dashboard. Yahoo access uses independent [yfinance WebSocket support](https://ranaroussi.github.io/yfinance/reference/yfinance.websocket.html); availability, delay, and data terms depend on Yahoo. Use for personal coursework only.
