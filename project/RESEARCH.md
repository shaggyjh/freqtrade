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
