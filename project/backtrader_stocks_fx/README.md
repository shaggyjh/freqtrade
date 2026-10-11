# Backtrader stocks + FX research (paper-only)

A separate Python/Backtrader research track alongside Freqtrade's Coinbase crypto experiments. **No broker connections, secrets, live orders, margin or leverage.**

## What's included
- Ordinary shares available to eligible UK brokerage accounts: AAPL, MSFT, SHEL.L and AZN.L. Eligibility and dealing availability must still be checked with the chosen broker. No US-domiciled ETFs are included.
- FX price proxies: EURUSD=X and GBPUSD=X. Yahoo daily OHLC is not executable FX bid/ask pricing, and this backtest ignores FX carry/rollover.
- Fixed SMA(20/100) long-only trend baseline; orders placed after completed close and filled at next open.
- 65% chronological development period and 35% holdout; the holdout has 110 bars of indicator warmup with trading disabled until its start.
- Assumed commission + slippage *per side*: equities 0.05% + 0.05%; FX 0.01% + 0.01%. UK ordinary shares additionally have an approximate 0.5% purchase-tax allowance modeled as 0.25% extra commission on each side (a conservative cost proxy, **not** exact tax timing). These are **illustrative**, not broker quotes.
- Return, maximum drawdown, closed trades, volatility and passive buy-and-hold comparison.
- GitHub Actions workflow on pull requests or manual dispatch, JSON report as workflow artifact.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r project/backtrader_stocks_fx/requirements.txt
python project/backtrader_stocks_fx/research.py
```

## Limitations and next research
The data feed is unofficial Yahoo Finance, can be unavailable/rate-limited, and may be revised. The daily price-proxy test is **not** proof of an executable or profitable strategy. It approximates UK stamp duty rather than charging it at the exact buy event, and does not simulate FX conversion, stock borrow, dividends beyond adjusted-price handling, intraday spreads, swap/rollover, market impact, taxes or actual brokerage minimums. No claims of prospective edge.

Before paper brokerage integration: choose a UK-accessible broker, validate UK-eligible stock instruments, replace proxy FX prices with broker bid/ask candles, model commissions/minimums, add historical holdouts and failure/reconciliation safeguards. Do not connect real brokerage credentials or deploy without user approval.
