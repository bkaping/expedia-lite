# Market workstation — Assignment 4.1

Local Vue + FastAPI + SQLite dashboard for Yahoo Finance streaming observations. **Part 4.1 only:** one-minute candlesticks, corresponding observed volume deltas, feed/source age, durable observation revisions, and recorded replay. No trading, indicators, or AI market decisions.

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

Open [localhost:5173](http://127.0.0.1:5173). Vite proxies HTTP **and WebSockets** under `/api` to port 8000. SQLite initializes automatically at `backend/data/market.db` (WAL, schema version 1); no manual SQL or Yahoo credential is required. Optional settings go in ignored root `.env`, using `.env.example`. No browser receives credentials. Bind to loopback only: feed controls are intended for a single trusted local user.

Choose AAPL, MSFT, or BTC-USD. Yahoo subscribes once in the backend, independently of browser tabs. The chart starts with real received observations; it does not invent historical candles. Stocks may be quiet outside market hours. Source age is measured from Yahoo's timestamp, separately from receipt time and browser connectivity. “Live” requires a source age and recent receipt within 30 seconds. Closed means the minute elapsed, not that every exchange trade was observed. Volume is an **observed change in Yahoo's cumulative counter**, with unknown/reset handling; crypto's rolling counter is not exchange trade volume. See [design limitations](docs/design.md).

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
npm --prefix frontend run build
# With the backend running and fresh BTC-USD observations available:
.venv/bin/python scripts/verify_market_live.py
```

[Verification and evidence](docs/assignment4-verification.md) distinguish deterministic fixtures from real-provider checks. [Schema/design](docs/design.md), [submission report](report.md), [AI disclosure](AI-USE.md), [selected prompts](prompts/selected-prompts.md), and [handoff](handoffs/current.md) explain the implementation.

The existing Assignment 3 Stillpoint prototype remains at `/stillpoint`; its canonical skill, browser-local support panel, and data boundaries are preserved. See the [archived README](docs/assignment3-readme.md) and [verification](docs/assignment3-verification.md).

Chart library: [TradingView Lightweight Charts](https://tradingview.github.io/lightweight-charts/docs), Apache 2.0. Copyright (с) 2025 TradingView, Inc. Chart attribution and a TradingView link are visible in the dashboard. Yahoo access uses independent [yfinance WebSocket support](https://ranaroussi.github.io/yfinance/reference/yfinance.websocket.html); availability, delay, and data terms depend on Yahoo. Use for personal coursework only.
