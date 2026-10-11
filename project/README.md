# Paper-only quant research — first milestone

This is a deliberately small experiment, not a production trading system. No live trading, no exchange API credentials, no leverage. We start with BTC/USDT and ETH/USDT on Coinbase, 1-hour candles, and a simple EMA crossover baseline.

## Non-negotiable simplicity rule
Do not add infrastructure, dashboards, AI agents, cloud services, extra risk layers or speculative requirements before the first real backtest is executed and reviewed. Fix actual defects; don't build for imagined future needs.

## Files
- `config.paper.json`: dry-run spot config, virtual 10,000 USDT, no keys, starts stopped.
- `strategies/SimpleTrend.py`: basic EMA 20/50 crossover, 4% ROI target and 8% stop loss (research defaults, not recommendations).

## Run the first historical backtest
Run these commands from the root of a Freqtrade installation with Python dependencies installed. No API keys are required for public historical candles.

```bash
freqtrade download-data --config project/config.paper.json --timeframes 1h --days 365
freqtrade backtesting --config project/config.paper.json --strategy-path project/strategies --strategy SimpleTrend --timerange 20251001-20261001
freqtrade lookahead-analysis --config project/config.paper.json --strategy-path project/strategies --strategy SimpleTrend --timerange 20251001-20261001
```

Dates are illustrative; data availability may require adjusting them. Run commands only after confirming installation. Do **not** use `freqtrade trade` yet. Backtest is historical simulation, while dry-run uses current exchange data without submitting real orders.

## Acceptance criteria
1. Backtest actually executes and produces a saved result.
2. Inspect trade count, return, drawdown, and fee assumptions.
3. Run lookahead-analysis and review warnings.
4. Do not call a strategy profitable without meaningful out-of-sample evidence.

## Current status
Files added to project branch. Configuration/strategy static review only; **no executed Freqtrade backtest yet**.
