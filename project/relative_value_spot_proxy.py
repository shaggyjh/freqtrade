"""Spot-only BTC test of ETH-rich signal, with cost and BTC-hold controls.

Research only: not market-neutral arbitrage or a Freqtrade execution simulation.
All entries occur at the next 6h candle open after a closed-candle signal.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from benchmark_buy_hold import load_candles


def evaluate(root: Path, fee: float) -> dict:
    btc = load_candles(root, "BTC")[["date", "open", "close"]].rename(
        columns={"open": "btc_open", "close": "btc_close"}
    )
    eth = load_candles(root, "ETH")[["date", "open", "close"]].rename(
        columns={"open": "eth_open", "close": "eth_close"}
    )
    df = btc.merge(eth, on="date", validate="one_to_one").sort_values("date").reset_index(drop=True)
    if len(df) < 120 or (df[["btc_open", "btc_close", "eth_open", "eth_close"]] <= 0).any().any():
        raise ValueError("Insufficient synchronized positive-price candles")
    if (df["date"].diff().dropna() != pd.Timedelta(hours=6)).any():
        raise ValueError("Non-contiguous 6h data")
    log_ratio = np.log(df["eth_close"] / df["btc_close"])
    mean = log_ratio.shift(1).rolling(60).mean()
    std = log_ratio.shift(1).rolling(60).std().replace(0, np.nan)
    rich = ((log_ratio - mean) / std > 2).fillna(False).to_numpy()

    # A single $100 BTC position, no leverage, fixed 28-candle holding period.
    # If signal at i close, buy i+1 open and exit i+29 open. Skip overlapping signals.
    trades = []
    last_exit = -1
    for i in np.flatnonzero(rich):
        entry_i, exit_i = int(i + 1), int(i + 29)
        if entry_i <= last_exit or exit_i >= len(df):
            continue
        entry = float(df.at[entry_i, "btc_open"])
        exit_ = float(df.at[exit_i, "btc_open"])
        net = 100 * (exit_ / entry) * (1 - fee) / (1 + fee) - 100
        trades.append({
            "signal_utc": df.at[i, "date"].isoformat(),
            "entry_utc": df.at[entry_i, "date"].isoformat(),
            "exit_utc": df.at[exit_i, "date"].isoformat(),
            "net_profit_usdt": round(net, 5),
        })
        last_exit = exit_i
    pnl = sum(t["net_profit_usdt"] for t in trades)
    # Exposure-matched BTC baseline: invest $100 over each identical interval
    # independently, regardless of the relative-value signal direction.
    # This equals signal-triggered BTC holding, NOT a full-period BTC benchmark.
    start, end = 0, len(df) - 1
    buy_hold_btc = 100 * (
        float(df.at[end, "btc_close"]) / float(df.at[start, "btc_open"])
    ) * (1 - fee) / (1 + fee) - 100
    buy_hold_eth = 100 * (
        float(df.at[end, "eth_close"]) / float(df.at[start, "eth_open"])
    ) * (1 - fee) / (1 + fee) - 100
    return {
        "research_only": True,
        "first_candle": df.at[0, "date"].isoformat(),
        "last_candle": df.at[end, "date"].isoformat(),
        "fee_per_side": fee,
        "stake_usdt": 100,
        "wallet_usdt": 10000,
        "trades": len(trades),
        "wins": sum(t["net_profit_usdt"] > 0 for t in trades),
        "net_profit_usdt": round(pnl, 4),
        "wallet_return_pct": round(pnl / 10000 * 100, 5),
        "btc_buy_hold_100_usdt_net": round(buy_hold_btc, 4),
        "eth_buy_hold_100_usdt_net": round(buy_hold_eth, 4),
        "trade_details": trades,
        "limitations": (
            "Directional BTC-only proxy, not arbitrage; no slippage/spread beyond fee "
            "proxy, intrabar stop-loss, funding or hedging. Full-period buy-hold has "
            "different exposure. Research data is not a prospective unseen test."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="user_data/data/coinbase")
    p.add_argument("--output", required=True)
    p.add_argument("--fee", type=float, default=0.007)
    args = p.parse_args()
    if not 0 <= args.fee < 1:
        p.error("Invalid fee")
    result = evaluate(Path(args.data_dir), args.fee)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
