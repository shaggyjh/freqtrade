# Paper-only research protocol (October 2026)

No real orders, exchange credentials, leverage, paid services, or live deployment.

## What we are testing
- **Baseline:** SimpleTrend 6h EMA20/50 crossovers, with a conservative 1.2% fee **per side**.
- **Time stability:** Three non-overlapping 90-day backtests, using a rolling last-year sample. A good full-year result alone is insufficient.
- **VolatilityFilteredTrend:** An EMA crossover is skipped if ATR/price exceeds 1.5 times its preceding 60-candle median. Hypothesis: excessive volatility reflects unstable crowds and causes whipsaws.
- **CrowdExhaustion:** A new 20-candle low, 2x prior median volume, large lower wick and bullish close, followed by another rising close. Hypothesis: forced or emotional selling can overshoot. OHLCV cannot identify liquidation or actual human intent.

All candidate tests are exploratory. Parameters were selected as hypotheses, not tuned to historical returns. The existing backtests and additional tests share the same historical data; this is **not** independent out-of-sample evidence. Do not select a winner based on these results alone.

## Evaluation
Compare each period's trade count, net profit, drawdown, win rate and profit factor, and compare with a simple equal-weight BTC/ETH buy-and-hold benchmark on the **same dates and with the same assumed costs**. Freqtrade's 'Market change' is not necessarily an executable, cost-adjusted buy-and-hold benchmark. Implement that benchmark separately before claiming outperformance. Also examine results with realistic spread/slippage assumptions and multiple market regimes. A small number of trades is not strong evidence.

## Research leads (not claims of a proven edge)
- Investor attention, representativeness bias and attention spillovers: Journal of International Money and Finance (2025), DOI 10.1016/j.jimonfin.2025.103391.
- Order flow and returns: Journal of Financial Markets (2026), DOI 10.1016/j.finmar.2026.101047. Requires richer data than our candles.
- Cryptocurrency risk-managed momentum: Finance Research Letters (2025), DOI 10.1016/j.frl.2025.107879.
- Momentum crashes: Financial Markets and Portfolio Management (2025), DOI 10.1007/s11408-025-00474-9.
- Out-of-sample overfitting: *The Training Set Delusion* (2025), SSRN 5797242; *How Much Sharpe is Illusory?* (2026), SSRN 7350238. Treat working papers as preliminary.

Further speculative ideas for future study, **not implemented**: attention saturation and subsequent silence, weekend versus weekday liquidity changes, asymmetric recovery after high-volume drawdowns, cross-asset delayed reaction, and market-wide synchronisation as a proxy for panic. Each needs an explicit falsifiable hypothesis and data-quality checks.

## Observed backtest results — 10 October 2026

Source: GitHub Actions paper-only comparison log supplied by the user. Fee assumption is **1.2% per side**; these are simulated results, not live fills. Test periods differ slightly because of indicator warmup, so compare cautiously.

| Strategy | Trades | Net USDT | Wallet return | Max closed-trade drawdown |
| --- | ---: | ---: | ---: | ---: |
| VolatilityFilteredTrend, 6h | 22 | -7.702 | -0.08% | 0.27% |
| CrowdExhaustion, 6h | 5 | -40.212 | -0.40% | 0.41% |
| AttentionAftershock, 6h | 41 | -112.684 | -1.13% | 1.13% |

VolatilityFilteredTrend's non-overlapping 90-day windows (6h, same fee) yielded **+13.362 USDT / 6 trades** (Jan 13–Apr 13), **-13.298 USDT / 4 trades** (Apr 13–Jul 12), and **+8.014 USDT / 6 trades** (Jul 12–Oct 10). These are regime-sensitivity clues, **not** independent confirmation or a dependable positive edge. AttentionAftershock is the weakest of these three in this run; CrowdExhaustion has only five trades. No strategy should be deployed based on these observations.

**Next experiment:** Compare the 6h baseline and volatility filter on identical timeranges with the same warmup, and add a fee-adjusted equal-weight BTC/ETH buy-and-hold benchmark. Then test across independent periods, with realistic slippage and no parameter selection on the evaluation sample. Do not loosen fees simply to manufacture a positive result.

## Phase 2 implementation and decision rules (11 October 2026)

**Objective:** seek positive net returns after realistic costs, without optimising against the same historical observations. No profitability promise. No live/paper deployment.

- The automated workflow now compares SimpleTrend 6h, VolatilityFilteredTrend 6h and a fee-adjusted two-position BTC/ETH holding control over the same three 90-day dates. The holding control invests $100 in each asset and keeps $9,800 cash, matching the strategies' wallet and per-position stake. Holding is **not** exposure-matched to a strategy that may spend most of its time in cash; compare risk and time-in-market before interpreting any excess return.
- Benchmark uses opening price of first 6h candle and closing price of final 6h candle, charging 1.2% on both legs. This is an idealised historical benchmark; it does not simulate slippage, bid-ask spreads or fills.
- The benchmark workflow change must be executed and its output checked before making a claim of relative performance. The earlier supplied log predates this benchmark.
- **Observed loss mechanism:** At 1.2% fees per side, SimpleTrend 6h had 12 ROI exits earning +48.576 USDT, 10 crossover-signal exits losing -53.786 USDT, and two stop losses losing -20.608 USDT; net -25.817 USDT. This motivates investigating *late exits and whipsaws*, not blindly changing the profit target. SimpleTrend 1h had 141 exit-signal exits totalling -523.558 USDT and only 26 ROI exits totalling +105.248 USDT; high turnover is particularly damaging. These figures are from the October 10 uploaded log.
- **Decision gate:** Keep a candidate only if it has positive after-cost results across multiple disjoint evaluation periods, reasonable drawdown, plausible execution costs, and better risk-adjusted performance than the holding control. With only 2 assets and a few dozen trades, do not treat an attractive result as statistically proven. If the gate fails, stay in research mode and report failure plainly.
- **Independent validation:** The existing 365-day sample has already influenced research decisions and cannot serve as a genuinely unseen test. Freeze parameters and acquire older, non-overlapping data (or await future data) before claiming out-of-sample validation. No strategy change should be selected by peeking at the validation period.
- **Next hypothesis to preregister:** exits are late because the 6h EMA20/50 reversal requires a large move; compare a single predetermined earlier-exit variant against the frozen baseline on a *development* window, then test on separate unseen history. Do not implement or tune the variant using the evaluation windows already inspected.

**Status:** Phase 2 tooling in progress; benchmark and independent validation are not yet executed/verified. Phase 2 is **not complete** and no profitable strategy is established.

## 11 October 2026: benchmark runner correction and attention research

- The uploaded 11 October run **did not produce a valid buy-and-hold benchmark**: the workflow called `python` through the Freqtrade image entrypoint, yielding `invalid choice: 'python'` three times. Fixed by setting Docker `--entrypoint python` and ensuring the benchmark result directories are writable. **Do not claim benchmark outperformance until the corrected workflow executes and the three JSON outputs are inspected.**
- AttentionAftershock ran for 340 days (2025-11-05 to 2026-10-11) with 41 trades, 9 wins, 32 losses, -112.684 USDT net (-1.13% wallet) at 1.2% fees per side. Exit-signal exits accounted for 30 losing trades, -128.508 USDT. This is negative evidence for the OHLCV aftershock proxy as specified, **not** evidence that public attention exhaustion fails.
- VolatilityFilteredTrend's **11 October** quarterly results: +13.362 USDT (6 trades), -12.071 USDT (4 trades), +8.014 USDT (6 trades). Do not conflate these dates/results with the earlier 10 October windows.

### Preregister a true-attention test before inspecting outcomes

**Data candidate:** Wikimedia Pageviews API daily article-view counts for Bitcoin and Ethereum pages, or timestamped public-news mention counts. This is a measure of *information-seeking activity*, not a complete measure of trader attention or sentiment. Confirm endpoint availability, article-name stability, missing days, bot filtering, timezone, revisions and historical coverage before testing. Do not fabricate or interpolate attention observations silently.

**Point-in-time rule:** Treat a UTC day's pageviews as unavailable for any trading signal until **at least 48 hours after that UTC day ends**, to allow for reporting lag. Use only data whose conservative availability timestamp precedes the close of the 6h decision candle. Never use same-day final pageview totals for intraday decisions. A 7-day trailing attention baseline must be computed only from previously available observations; all thresholds and horizons must be fixed before examining returns.

**Hypothesis:** A spike in previously available public attention, followed by a decline in attention while price attempts to extend the prior move, predicts weaker forward 6h-to-7d risk-adjusted returns than comparable momentum events without the spike. Also test the opposite hypothesis (attention persistence). Separate BTC and ETH, compare against momentum, volatility and market-regime controls; report event counts, overlap, fee-adjusted returns and uncertainty, including null findings. Daily attention limits timing precision; this test cannot establish what traders knew in real time without verified publication timestamps.

**Validation:** First audit the attention feed and point-in-time joins; freeze the event definition; run development and genuinely held-out time periods. The already inspected 2025–26 price history is not independent validation. No live orders or paper deployment.
