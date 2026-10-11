# Structural-edge research queue — 2026-10-11

All work remains paper-only, Coinbase spot, no credentials, leverage, futures, or deployment.

## Why shift direction?
EMA crossovers, OHLCV-only attention proxies and the BTC-only relative-value proxy have not produced viable cost-adjusted results. Prior BTC/ETH relative-value results measured **relative** price movement and could not be captured with our long-only bot. Do not fit parameters to those outcomes.

## Candidate tests, in execution-feasibility order

### 1. Volatility compression to expansion (OHLCV available)
Hypothesis: breakouts after unusually compressed realized ranges persist more often than generic breakouts, even after taker fees.
Freeze candidate before measuring: Coinbase BTC/USDT and ETH/USDT 6h; previous 20 candles' high-low range normalized by close; compare current range with the previous 120-candle distribution, shifted by one. Signal at 6h close only when prior range is in the lowest decile and close exceeds prior 20-candle high with volume above trailing 20-candle median. Enter no earlier than next candle open. Test 4/12/28-candle exits and a fixed ATR stop only as separately declared variants, not post-hoc optimized choices. Baselines: all 20-candle breakouts, BTC/ETH buy-and-hold, and cash. Include 0.5%, 0.7%, 1.2% per-side fee scenarios and a spread/slippage sensitivity. Require event counts, max drawdown, exposure, and multiple market regimes.

### 2. Panic stabilization / failed breakdown (OHLCV proxy only)
Hypothesis: after a large downside candle, reclaim of a previous support level predicts positive *absolute* spot returns. This is **not** evidence of forced liquidation without timestamped liquidation data. Predeclare signals before backtesting; distinguish from existing FailedBreakout strategy.

### 3. Calendar / time-of-week conditional returns (OHLCV available)
Predeclare UTC hour and weekend buckets. Avoid optimizing dozens of time buckets. Compare event returns against volatility/exposure-matched controls. Correct for multiple tests; fees may dominate.

### 4. Funding / positioning extremes (new external data required)
Require historical contract-specific funding, open interest and publication timestamps. Measure whether extreme funding predicts **spot** returns. Funding yield itself needs hedged legs and cannot be assumed executable in spot-only Freqtrade.

### 5. ETF/on-chain flow (new external data required)
Use timestamped, historically available reports with a publication lag. Separate true deposits to exchanges from ordinary wallet transfers; reject revised or incomplete feeds.

### 6. Adaptive regime selection
Only after individual strategy families have separately demonstrated repeatable edge. Freeze the selector on training data, evaluate in walk-forward windows and report strategy-selection overfit risk.

## Evaluation safeguards
- Historical sample already inspected (2025–26) is exploratory; use older distinct ranges and then prospective paper-only tracking.
- No claims of profitability based on gross price movements or statistical significance alone.
- Avoid HFT latency-arbitrage claims based on six-hour candles.
- Compare on equal capital, equal exposure where practical, net fees, slippage assumptions, drawdown, trade count, and turnover.
- Stop testing an idea if executable long-only returns remain negative across validation periods.
