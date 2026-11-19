# Assignment 4.2 verification — November 19, 2026

## Automated behavior and references

- **50 backend tests pass**: 33 preserved tests plus 17 Part 4.2 cases in [test_strategy.py](../backend/tests/test_strategy.py).
- **2 frontend indicator tests pass**: `node --test frontend/src/indicators.test.js`.
- **Production frontend build passes**: `npm --prefix frontend run build`.
- No dependency was added. pandas 3.1.1, already installed via yfinance 1.8.0, serves as an independent rolling-window reference.

The backend checks cover the [published TradingView 3-period SMA example](https://www.tradingview.com/support/solutions/43000502589-moving-averages/) ([5,6,7,8,9] → [6,7,8]), explicit known crossover indices, and 1,200 seeded prices across 2/3, 5/20 and 20/100 windows. Independent batch, incremental Decimal-sum and [pandas rolling](https://pandas.pydata.org/docs/reference/api/pandas.Series.rolling.html) values/crossovers agree within 1e-9. The equality tolerance and warm-up convention are documented, rather than silently assuming a first warm-up relationship is a crossover.

Further checks verify that unfinished outliers neither trade nor affect confirmed indicators/marks; altering future prices leaves earlier signals/equity unchanged; a last-bar order remains pending; every historical fill uses a later bar's open; live fills reject pre-signal receipts and use the actual eligible quote instead of a stale bar open. Dataset validation rejects overlapping/unfinished/malformed history. Restarted incremental state matches uninterrupted processing, saved runs reopen identically, paper cursors avoid duplicate fills, and late closed-candle corrections do not rewrite the account. Active-account replacement is rejected and stopping cancels pending orders. Live position marks update with new quotes even without another order.

## Known accounting example

$1,000 cash, no slippage, $1 fee per fill: buy at $100 → 9.99 units, $1,000 entry basis, zero cash. At $110: equity $1,098.90, unrealized P/L $98.90. Sell at $120: cash/equity $1,197.80, realized P/L $197.80, fees $2, no remaining position. Tests verify these exact values, nonzero adverse slippage, no negative cash/short position, insufficient-cash skips, Decimal restoration, and equity = cash + market value = initial cash + realized + unrealized P/L.

These are deliberately artificial test examples, distinct from the real Yahoo run below.

## Genuine Yahoo historical capture and saved API run

The [included snapshot](assignment4-part2-evidence/yahoo-hourly-sample.json) was fetched from Yahoo using the existing yfinance history API at **14:44:25 UTC / 09:44:25 Eastern**. AAPL, one month of unadjusted regular-session hourly OHLCV, 161 completed bars; dataset hash `44e37cd3c962fa3baec80b76b5460a86be9dd819960fa5817843ff0878b0fc7c`. It is a downloaded historical dataset, not new streaming ticks or generated fixture data. Source, fetch time and completion boundary are stored with it.

[scripts/verify_strategy.py](../scripts/verify_strategy.py) explicitly loads that sample through FastAPI, creates/reopens a backtest, compares all SMA values/crossovers with pandas and checks every fill's causal timestamp and account identities. [Machine-readable evidence](assignment4-part2-evidence/api-verification.json) records maximum SMA error **5.684341886080802e-14**, exact saved-run reopening, all crossover agreement, later fill times, accounting identities, and invalid-window HTTP 422.

Default assumptions: SMA 5/20; $10,000 initial cash; $1 fee per fill; 5 bps adverse slippage; fractional units truncated to six decimals. Observed result:

| Measure | Result |
|---|---:|
| Orders / fills / completed exits | 10 / 9 / 4 |
| Equity | $9,615.637271934265 |
| Cash rounding residue | $0.0002104335014 |
| Open AAPL units | 27.294663 |
| Realized P/L | −$345.7854371534211 |
| Unrealized P/L | −$38.57729091231387 |
| Fees | $9 |
| Return | −3.84362728065735% |
| Maximum completed-bar drawdown | 5.920415786849465% |

The initial SELL was skipped because the account was flat. The ending position is marked, not forcibly sold. The loss was retained; parameters were not searched to produce a profitable result. This one sample establishes reproducibility under the declared assumptions, not predictive performance.

## Browser and push-triggered CI

The first actual [GitHub Actions run](https://github.com/bkaping/expedia-lite/actions/runs/44548261750) passed for implementation commit `dc41ceb0f186ab8172f474fc5a7658f625f530ef`, including the automated [Chrome browser regression](../scripts/browser_smoke.py). The workflow runs backend tests, frontend indicator tests, production build, and real DOM interactions on every push/PR. Its live feed is deliberately disabled; the UI explicitly loads the genuine recorded Yahoo sample. No new browser package was installed; Chrome/ChromeDriver come with the GitHub Ubuntu runner.

The persistent browser regression verifies historical mode, sample loading, 161 bars, SMA readouts, 9 fills and −3.84% return, BUY/SELL history, invalid-window error, and forward paper start/stop. Local computer-use checks additionally verified chart lines/markers, dataset identity, saved performance, keyboard controls and responsive behavior. Screenshots:

- [SMA chart and crossovers](assignment4-part2-evidence/indicators-dashboard.png).
- [Backtest account and equity](assignment4-part2-evidence/backtest-account.png).
- [Orders and fills](assignment4-part2-evidence/fills-table.png).
- [Forward paper account](assignment4-part2-evidence/paper-account.png).

[The 40-second video](assignment4-part2-evidence/part4-2-demo.mp4) combines actual browser captures at one frame/second with segment cuts and captions: 0–10s historical SMA/crossover chart; 10–20s saved account/equity; 20–30s signal/fill audit trail; 30–40s forward paper account and explicit stop. No new confirmed crossover occurred during the paper-account clip, so no live paper fill is claimed. Historical trades are genuine simulation results on recorded Yahoo prices; the separate paper engine's fill behavior is verified by deterministic receipt-order tests. The video briefly explains next-open causality and reference/accounting checks. [Encoder source](../scripts/create_strategy_demo.swift) uses built-in macOS AVFoundation.

## Revised approaches and limits

The first synthetic fixture used a zero low; production validation correctly rejected it. The fixture was fixed to positive, consistent OHLC rather than weakening validation. A later test accidentally advanced the clock enough to close another candle while checking a late correction; receipt timing was corrected to isolate the intended behavior. The more substantive design revision separated historical next-open execution from forward received-quote execution: blindly reusing the former could fill a paper order at an open known before its signal. Tests now establish that distinction.

See [design](design.md) for exact ledger formulas, warm-up/provisional rules, data gaps, price corrections, costs and bias limits. Historical Yahoo data is not a point-in-time archive; current surviving-symbol selection can create survivorship bias; repeated parameter selection risks overfitting. Unadjusted bars omit credited dividends/splits, fixed slippage omits liquidity/latency/partial fills, and no out-of-sample profitability is established. All trading is local and simulated; Part 4.3 AI/audio is not implemented.

Final clean-source verification: implementation commit `3cb1c52b26dea7ce42731fda5879eb81290f47fe` was extracted with `git archive`. All 50 backend tests passed using the installed project Python interpreter. A fresh `npm ci`, two Node indicator tests and production build also passed. This did not reinstall Python dependencies. The final video was decoded for representative-frame inspection and measured at exactly 40.0 seconds. Pinned README, video and API evidence URLs returned unauthenticated HTTP 200.

The final implementation’s [push-triggered GitHub Actions run 44550305626](https://github.com/bkaping/expedia-lite/actions/runs/44550305626) completed successfully for `3cb1c52b26dea7ce42731fda5879eb81290f47fe`, including the Chrome browser regression. [Saved public CI metadata](assignment4-part2-evidence/ci-verification.json) records that result.
