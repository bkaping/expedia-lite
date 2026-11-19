# Part 4.1 verification — November 19, 2026

## Deterministic checks

` .venv/bin/python -m unittest discover -s backend/tests -v `: **33 passing**, including 11 new market tests. `npm --prefix frontend run build`: **pass**. `pip check`: no broken requirements. yfinance 1.8.0 and Lightweight Charts 5.3.0 installed after student approval; no model/API key added.

Market fixtures in [test_market.py](../backend/tests/test_market.py) verify:

- Identical latest payload adds a receipt only, without double-counting volume.
- Changed payload retains both raw revisions and repairs high/close/volume.
- Late source timestamps determine open/close by source order, with subsequent volume-baseline repair.
- Interval closure persists without another tick; late correction keeps the candle closed.
- Unknown volume, first baselines and decreasing counter resets do not invent volume.
- Replay prefixes exclude future revisions; one-event pagination reproduces current saved state.
- Restart preserves observations/events; repeated initialization and duplicate detection remain valid.
- Invalid observations do not write; connected-but-no-fresh-symbol differs from unavailable.

A focused recheck with ResourceWarning enabled also confirmed the market connection context manager closes SQLite handles after commit/rollback. These artificial fixtures test behavior; they do not demonstrate a live market connection.

## Real Yahoo / SQLite / WebSocket path

[Machine-readable live verification](assignment4-evidence/live-verification.json), produced by [verify_market_live.py](../scripts/verify_market_live.py), records actual Yahoo BTC-USD observations at 14:20:58 UTC (09:20:58 Eastern). Event #36's OHLCV/complete/source-time matched its SQLite row exactly. Source age was about 4.15 seconds; browser snapshots came over FastAPI WebSockets. Deliberately disabling the feed reported `unavailable` and retained two stored candles. Replay played 19 saved candle revisions through boundary #36 and matched SQLite's state at that boundary. Feed was restored in a `finally` block.

The automated script reads the real running backend, not an injected source or mock. Yahoo subscribed to AAPL, MSFT, and BTC-USD; premarket stock observations were intermittent and some omitted volume. Crypto's supplied counter was unchanged during portions of this check, so displayed volume deltas were zero. No claim of complete exchange trades or accurate per-minute crypto trading volume is made.

## Browser and recording

- [Live dashboard](assignment4-evidence/live-dashboard.png): real prices, source age, live status, OHLC candles, observed-volume layer, revision counts and persisted table.
- [Unavailable feed](assignment4-evidence/unavailable-dashboard.png): source disconnected, age increases, saved candles remain visible, backend still connected.
- [Backend offline](assignment4-evidence/backend-offline-dashboard.png): after stopping FastAPI, saved candles remained visible through automatic reconnect attempts; the browser labeled the backend offline. The API was then restored.
- [Recorded replay](assignment4-evidence/replay-dashboard.png): explicit recorded-data banner, ordered saved revisions, closed/forming historical flags and replay completion.
- [40-second video](assignment4-evidence/part4-1-demo.mp4): 0–12s actual live observations; 12–20s unavailable-source condition; 20–32s saved revision replay; 32–40s source restoration. Captions identify commit-before-display and fixed-boundary replay as design/verification choices. Silent, actual browser captures sampled at 1 frame/second, with cuts between interaction segments; encoded using macOS AVFoundation via [the reproducible encoder](../scripts/create_market_demo.swift). Not a continuous high-frame-rate screen recording and not synthetic chart animation.

Desktop layout checked at 1440px; 390px layout had no document overflow (390px viewport and document width), and Enter activated both replay/live controls. The initial chart resize warning was removed by using the chart library’s built-in auto-sizing alone. Semantic controls have visible focus; equivalent OHLCV values appear in a readable table. No motion is required to interpret the market chart; the previous breathing app retains its reduced-motion alternative. Browser-console and responsive results are described only to the extent checked.

## Offline reproduction

The included [Yahoo recording](assignment4-evidence/yahoo-observations.jsonl) contains 99 original public receipts, captured through about 14:25 UTC. Import into a new temporary SQLite DB passed and produced at least three BTC-USD candles. This demonstrates source-data reconstruction and replay without a live market, not a new live connection. See [startup/import steps](../README.md).

## Failed approach → evidence → revision

The first live-source run raised `SSLCertVerificationError` because the Python.org macOS installation had no usable default trusted CA bundle. Unit tests and chart build could not establish source connectivity. Generated code in [feed.py](../backend/app/market/feed.py) now sets the process's `SSL_CERT_FILE` to already-installed `certifi.where()` only if no explicit bundle is configured. TLS certificate verification stays enabled. Subsequent genuine Yahoo receipts and the socket/SQLite comparison established that this fix enabled the source path. This does not guarantee future availability.

## Remaining limits and submission

See [design](design.md): timestamp identity ambiguity, partial observed candles, volume limitations, server-clock assumptions, low-rate full-history recomputation, no retention/authentication, and no market delay guarantee. The report and video must identify the actual submitted commit; instructor access must be confirmed. Canvas receives **only `report.md`**, with repository, commit, one 30–60-second video, supporting links, and [AI disclosure](../AI-USE.md). No indicators, simulated trading, backtesting, or AI market interaction is claimed in Part 4.1.

Final-code repeat at 14:29:15 UTC: [final live verification](assignment4-evidence/final-live-verification.json) matched event #244 to SQLite, retained 11 candles with the feed unavailable, and replayed 114 candle revisions through boundary #245 to the same final database state. The earlier event #36 evidence and video remain separate observations.

Clean Git archive verification passed all 33 tests using the already-installed project Python environment; a fresh `npm ci` followed by a production build also passed. The archive contained no root `.env`, generated database, or frontend node_modules. This was not a fresh Python dependency installation.
