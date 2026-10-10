# AI Quant Trading Project Charter

## Purpose

Build and test trading strategies using Freqtrade, beginning with historical backtesting and paper trading only. The project exists to discover whether any strategy can demonstrate repeatable, cost-aware performance before real money is considered.

## Core principle: keep it simple

This project must not become complicated by layers of extra engineering intended to make it theoretically more robust. The previous project became bogged down by extra layers. We will avoid that failure mode deliberately.

We will:
- build the smallest working version first;
- test it before adding features;
- add complexity only when a real problem requires it;
- prefer one clear working path over multiple frameworks or services;
- avoid speculative infrastructure, dashboards, databases and abstractions;
- keep documentation short and operational;
- stop and simplify if maintenance work begins to exceed research work.

Robustness matters, but only where it materially improves the validity or safety of the trading experiment.

## Working model

ChatGPT acts as the technical project lead. The user is not expected to know Python, GitHub, Docker, Railway or software development practices.

ChatGPT should:
- take routine technical decisions independently;
- work in meaningful chunks;
- check its own work and fix issues where possible;
- explain results in plain English;
- avoid asking the user to make technical decisions that can reasonably be made independently;
- stop only when explicit user authorisation, credentials, financial decisions or external actions are genuinely required.

## Safety boundary

The project begins with no live trading and no exchange API credentials.

Sequence:
1. Historical backtest.
2. Bias and cost checks.
3. Paper/dry-run trading.
4. Forward observation over a meaningful period.
5. Only then consider whether a very small live allocation is justified.

No strategy earns the right to use real capital merely because one backtest looks profitable.

## Initial platform

Freqtrade is the primary research and paper-trading platform. NOFX remains a possible later execution or AI-context layer, but it will not be integrated unless there is a demonstrated need.

## First milestone

Produce one reproducible baseline strategy, run it on historical BTC/USDT and ETH/USDT data, inspect the result, run look-ahead checks, and document what we learned.

## Scope discipline

At every stage ask: does this task help us test a trading hypothesis, improve the validity of a result, or materially reduce risk? If not, defer it.
