# Arbitrage and alternative-data research protocol — 11 October 2026

Research only. No exchange changes, futures access, short orders, leverage, credentials, or deployment.

## Ranked hypotheses

1. **BTC/ETH relative-value mean reversion**: test whether an unusually high ETH/BTC price ratio predicts ETH underperformance relative to BTC over the next 1–7 days. An economically market-neutral implementation needs simultaneous long and short legs; our Coinbase spot-only Freqtrade configuration **cannot** execute the short leg. First test a long-only *rotation or cash* proxy as a separate, directional strategy. Do not call this arbitrage or equate it with hedged pairs-trading P&L.
2. **Public attention and microstructure**: audit timestamped Wikipedia pageviews, exchange order-book snapshots and, if available, exchange inflow data. Pageviews are not actual order flow; blockchain transfers are not necessarily exchange deposits. Apply publication/ingestion lags and reject incomplete or non-point-in-time feeds.
3. **Spot/futures basis**: theoretical gross yield equals convergence of futures premium for dated futures, minus both-leg commissions, spread, funding/borrow/collateral, slippage, liquidation and counterparty costs. For perpetual swaps, funding is variable and can reverse; there is no guaranteed convergence at maturity. Require historical simultaneous spot/derivatives quotes, mark prices, funding histories and margin stress scenarios before estimating yield.
4. **Funding capture**: calculate realized historical funding cashflows with timestamps, sign, margin usage, both-leg execution costs, exchange outages and liquidation stress. Positive quoted funding is not a locked-in return.
5. **Options VRP**: needs historical option chains, bid/ask IV surface, realized hedging costs, jumps, expiries and margin; out of scope of our existing OHLCV-only backtest.
6. **Cross-venue latency arbitrage**: no HFT performance claims from candle data. Requires simultaneous timestamped order books and measured end-to-end execution latency; deprioritize.

## Preregistered BTC/ETH relative-value diagnostic

Use synchronized Coinbase 6h candles and only information available at signal close. Ratio is ETH/USDT close divided by BTC/USDT close. At each 6h close, calculate the trailing 60-candle mean and standard deviation of log ratio using **prior candles only** (shift by one). Events: z-score above +2 or below -2, with at least 28 candles between counted events. Test whether ratio moves toward its trailing mean over 4, 12 and 28 subsequent candles; report each direction separately, counts, mean/median changes, uncertainty and non-overlap. Do not trade at the signal candle's closing price: simulated fills begin next candle and include fee, spread, slippage, and an unhedged-market control. If there are fewer than 30 independent events per direction, mark evidence insufficient. Avoid choosing threshold/horizon after viewing outcomes.

**Crucial:** historical 2025–26 data has already been inspected. This is a *development* sample only. Freeze logic before checking separate, older untouched data or accumulating future paper data. Any eventual long-only proxy must be tested independently, and compared with both BTC and ETH buy-and-hold on exposure-matched capital.

## Existing baseline

RegimeGatedTrend (6h, approximately 340 days) generated 5 trades and lost 1.890 USDT at 0.5% per-side fees, 2.642 USDT at 0.7%, and 4.522 USDT at 1.2%. VolatilityFilteredTrend generated 22 trades, +9.820, +6.390, and -7.702 USDT respectively. Neither supports deployment; filter tuning on this same period would be overfitting.

## Implementation limits

Freqtrade documents that spot trading cannot short; its futures mode is supported only for selected exchanges. A two-leg hedge across instruments/venues needs explicit coordination, fill reconciliation and collateral management beyond our current single-position spot configuration. Never implement synthetic hedging by simply opening two unrelated long positions.

Sources: https://www.freqtrade.io/en/2026.5/leverage/ ; https://www.freqtrade.io/en/latest/ ; https://link.springer.com/article/10.1007/s10203-021-00318-x ; https://www.sciencedirect.com/science/article/pii/S154461232401393X
