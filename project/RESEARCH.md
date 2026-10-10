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
