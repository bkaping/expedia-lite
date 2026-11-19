# Assignment 4, Part 1 — Market Data and the Dashboard

Completed November 19, 2026. **Scope: Part 4.1 only.**

**Repository:** [bkaping/expedia-lite](https://github.com/bkaping/expedia-lite/tree/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f). **Submitted implementation and evidence commit:** [`b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f`](https://github.com/bkaping/expedia-lite/commit/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f), branch `codex/assignment4-1`. This report is saved separately after pinning that implementation commit.

**Video:** [Watch/download the 40-second Part 4.1 demonstration](https://raw.githubusercontent.com/bkaping/expedia-lite/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/docs/assignment4-evidence/part4-1-demo.mp4). One silent, captioned video of actual browser captures sampled once per second, with cuts between segments: live Yahoo observations, deliberate feed disconnection, saved revision replay, and reconnection. Captions explain commit-before-display and fixed-boundary replay. It contains no generated chart animation.

## Completed functionality and decisions

Vue displays updating one-minute candlesticks and corresponding observed-volume deltas using Lightweight Charts. FastAPI maintains a real Yahoo Finance WebSocket subscription for AAPL, MSFT, and BTC-USD; a separate backend-to-browser WebSocket delivers saved chart states. Source, source age, receipt/event time, connection status, closed/forming state, and record revisions are visible. The former Assignment 3 application is preserved at `/stillpoint`.

SQLite stores immutable source revisions, every valid receipt including duplicates, and versioned candle states. Identical latest payloads add a receipt without double-counting; changed payloads create revisions. Late observations repair OHLC in source-time order and affected volume baselines. A timer persists interval closure even without another tick. Replay starts empty, applies saved revisions in receipt order, and stops at a captured event boundary, excluding future live arrivals. [Design and schema](https://github.com/bkaping/expedia-lite/blob/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/docs/design.md) explain these rules and identity ambiguity.

## Verification and process

All **33 backend tests**, including 11 market cases, pass; the production frontend build passes. A clean Git archive passed the backend suite using the installed project Python environment and a fresh `npm ci`/production build. Recording import into a new database also passed. Desktop/mobile layout and keyboard mode controls were checked.

The final **real-provider** check matched WebSocket event #244 exactly to its SQLite candle, with source age about 5.8 seconds. Disconnection retained 11 candles; replay applied 114 revisions through boundary #245 and matched the database state at that boundary. Backend shutdown/reconnect also retained visible candles. Artificial test fixtures are distinct from these real-provider observations. [Verification, screenshots, and machine-readable evidence](https://github.com/bkaping/expedia-lite/blob/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/docs/assignment4-verification.md).

One revised approach: the initial live connection failed with a certificate-verification error. Supplying the existing certifi trusted CA bundle in generated `backend/app/market/feed.py` enabled genuine Yahoo receipts while preserving TLS verification. SQLite connection cleanup was also corrected after ResourceWarning evidence. [Curated process evidence](https://github.com/bkaping/expedia-lite/blob/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/docs/evidence-log.md), [selected instructions](https://github.com/bkaping/expedia-lite/blob/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/prompts/selected-prompts.md), and [AI-use disclosure](https://github.com/bkaping/expedia-lite/blob/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/AI-USE.md) document Codex's role and the student's dependency approval.

## Limitations and reproduction

Yahoo availability/delay is not guaranteed. These are observed-price candles, not a full exchange trade tape; a closed interval may have gaps or later corrections. Timestamp-derived identity cannot distinguish every same-millisecond trade from a revision. Volume is a best-effort cumulative-counter delta: unknown/reset handling is explicit, and crypto's rolling USD counter is not exact traded quantity. During the captured demo its deltas were zero; some premarket stock messages omitted volume. These observations do not establish exchange-quality OHLCV.

This is a local, single-process coursework prototype with no authentication, retention policy, or high-throughput guarantee. Indicators, trading, backtesting, AI decisions and audio belong to later parts and are not implemented here. [README startup and offline replay](https://github.com/bkaping/expedia-lite/blob/b37adf29ca9ac99e2fe6f12eebd10ad0d5a70a4f/README.md) describe automatic database initialization, ignored DB files, and credential-free Yahoo startup. Credentials remain in ignored root `.env`.

The pinned README, final evidence, and video URLs were checked without authentication and returned HTTP 200 on November 19, 2026.

Upload **only this `report.md`** to Canvas. Source code and evidence remain in the linked public GitHub repository; the video link refers to the same pinned version.
