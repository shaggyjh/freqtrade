"""Research-only Backtrader stock/FX comparison. No brokerage connections or orders.

Downloads daily Yahoo Finance research data (unofficial, not execution-quality).
Signals are calculated at a completed daily close; orders fill next session open.
The final 35% of observations is a chronological holdout, not a fitted model.
"""
import argparse
import json
from pathlib import Path

import backtrader as bt
import numpy as np
import pandas as pd
import yfinance as yf

ASSETS = {
    "AAPL": {"symbol": "AAPL", "market": "us_stock", "commission": 0.0005, "slippage": 0.0005},
    "MSFT": {"symbol": "MSFT", "market": "us_stock", "commission": 0.0005, "slippage": 0.0005},
    "SHEL_L": {"symbol": "SHEL.L", "market": "uk_stock", "commission": 0.0005, "slippage": 0.0008, "uk_stamp_duty_buy": 0.005},
    "AZN_L": {"symbol": "AZN.L", "market": "uk_stock", "commission": 0.0005, "slippage": 0.0008, "uk_stamp_duty_buy": 0.005},
    "EURUSD": {"symbol": "EURUSD=X", "market": "spot_fx_proxy", "commission": 0.0001, "slippage": 0.0001},
    "GBPUSD": {"symbol": "GBPUSD=X", "market": "spot_fx_proxy", "commission": 0.0001, "slippage": 0.0001},
}
START_CASH = 10000.0


class Trend(bt.Strategy):
    params = dict(fast=20, slow=100, allocation=0.95, trade_start=None)

    def __init__(self):
        self.fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        self.slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.pending = None

    def notify_order(self, order):
        if order.status in (order.Completed, order.Canceled, order.Margin, order.Rejected, order.Expired):
            self.pending = None

    def next(self):
        if self.p.trade_start is not None and self.data.datetime.date(0) < self.p.trade_start:
            return
        if self.pending:
            return
        if not self.position and self.fast[0] > self.slow[0] and self.fast[-1] <= self.slow[-1]:
            # Conservative cash buffer for fees, slippage and price gaps.
            size = self.broker.getcash() * self.p.allocation / self.data.close[0]
            self.pending = self.buy(size=size)
        elif self.position and self.fast[0] < self.slow[0]:
            self.pending = self.close()


def download(symbol: str, start: str, end: str) -> pd.DataFrame:
    frame = yf.download(symbol, start=start, end=end, auto_adjust=True, progress=False, threads=False)
    if frame.empty:
        raise ValueError(f"No daily observations for {symbol}")
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.rename(columns=str.lower)
    required = ["open", "high", "low", "close", "volume"]
    for field in required:
        if field not in frame:
            if field == "volume":
                frame[field] = 0
            else:
                raise ValueError(f"Missing {field} for {symbol}")
    frame = frame[required].copy().dropna(subset=["open", "high", "low", "close"])
    frame.index = pd.to_datetime(frame.index).tz_localize(None) if frame.index.tz is None else pd.to_datetime(frame.index).tz_convert(None)
    frame = frame[~frame.index.duplicated(keep="last")].sort_index()
    if len(frame) < 320:
        raise ValueError(f"Insufficient history for {symbol}: {len(frame)} rows")
    return frame


def simulate(frame: pd.DataFrame, commission: float, slippage: float, trade_start=None, buy_tax: float = 0.0) -> dict:
    engine = bt.Cerebro(stdstats=False)
    engine.adddata(bt.feeds.PandasData(dataname=frame))
    engine.addstrategy(Trend, trade_start=trade_start)
    engine.broker.setcash(START_CASH)
    engine.broker.setcommission(commission=commission + buy_tax / 2)  # Conservative round-trip tax proxy; real UK SDRT applies on buys only.
    engine.broker.set_slippage_perc(perc=slippage, slip_open=True, slip_match=True)
    engine.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    engine.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    engine.addanalyzer(bt.analyzers.TimeReturn, _name="daily", timeframe=bt.TimeFrame.Days)
    strategy = engine.run()[0]
    final = float(engine.broker.getvalue())
    trade_stats = strategy.analyzers.trades.get_analysis()
    returns = strategy.analyzers.daily.get_analysis()
    daily = pd.Series({pd.Timestamp(k): v for k, v in returns.items()}, dtype=float).sort_index()
    max_dd = float(strategy.analyzers.drawdown.get_analysis().max.drawdown)
    # Same commission/slippage assumptions for passive benchmark, using first open / last close.
    start_index = frame.index.searchsorted(pd.Timestamp(trade_start)) if trade_start is not None else 0
    benchmark = START_CASH * (frame.close.iloc[-1] / frame.open.iloc[start_index]) * (1 - commission - slippage) / (1 + commission + slippage + buy_tax)
    return {
        "initial_cash": START_CASH,
        "ending_equity": round(final, 2),
        "net_return_pct": round((final / START_CASH - 1) * 100, 3),
        "max_drawdown_pct": round(max_dd, 3),
        "closed_trades": int(trade_stats.get("total", {}).get("closed", 0)),
        "buy_hold_net_return_pct": round((benchmark / START_CASH - 1) * 100, 3),
        "daily_return_count": len(daily),
        "daily_volatility_pct": round(float(daily.std() * np.sqrt(252) * 100), 3) if len(daily) > 1 else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2026-10-11")
    parser.add_argument("--output", default="project/backtrader_stocks_fx/results/report.json")
    args = parser.parse_args()
    report = {"research_only": True, "execution": "Backtrader next-session open; no live broker",
              "data_source": "Unofficial Yahoo Finance adjusted daily OHLC, may be revised or unavailable",
              "limitations": "No shorting, leverage, borrowing, FX swap/rollover, financing, FX conversion, market-hours microstructure, detailed taxes, survivorship correction or execution-quality bid/ask. UK SDRT is approximated by splitting a 0.5% buy tax over both sides, not modeled at the actual purchase event. FX is an unlevered USD-quote price proxy, not a realistic broker account. Commission/slippage are illustrative assumptions, not broker quotes.",
              "assets": {}}
    for name, cfg in ASSETS.items():
        try:
            frame = download(cfg["symbol"], args.start, args.end)
            # Fixed chronological split. Include warmup from prior history for holdout.
            cut = int(len(frame) * 0.65)
            warmup = 110
            development = frame.iloc[:cut].copy()
            holdout = frame.iloc[max(0, cut - warmup):].copy()
            report["assets"][name] = {
                "market": cfg["market"], "ticker": cfg["symbol"],
                "cost_per_side": {"commission": cfg["commission"], "slippage": cfg["slippage"]},
                "uk_buy_tax": cfg.get("uk_stamp_duty_buy", 0.0),
                "development": {"start": str(development.index[0].date()), "end": str(development.index[-1].date()),
                                **simulate(development, cfg["commission"], cfg["slippage"], buy_tax=cfg.get("uk_stamp_duty_buy", 0.0))},
                "holdout": {"start": str(frame.index[cut].date()), "end": str(frame.index[-1].date()),
                            "warmup_bars": cut - max(0, cut - warmup),
                            **simulate(holdout, cfg["commission"], cfg["slippage"], frame.index[cut].date(), cfg.get("uk_stamp_duty_buy", 0.0))},
            }
        except Exception as exc:
            report["assets"][name] = {"error": str(exc)}
    if all("error" in v for v in report["assets"].values()):
        raise RuntimeError("All asset downloads or simulations failed: " + json.dumps(report["assets"]))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
