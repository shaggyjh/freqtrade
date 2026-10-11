"""Cost-adjusted, equal-weight BTC/ETH spot buy-and-hold control.

Run inside Freqtrade's Docker image after download-data. Each asset receives a
single $100 entry, matching the strategy's stake size and two-trade maximum.
Remaining $9,800 stays cash. No leverage or rebalancing. Same 1.2% fee per side.
This is a benchmark, NOT an execution-equivalent simulation of limit fills.
"""
import argparse
import json
from pathlib import Path

import pandas as pd


def load_candles(root: Path, asset: str) -> pd.DataFrame:
    files = sorted(root.rglob(f"{asset}_USDT-6h.feather"))
    if len(files) != 1:
        raise RuntimeError(f"Expected exactly one {asset} 6h feather file in {root}; got {files}")
    frame = pd.read_feather(files[0])
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    return frame.sort_values("date")


def benchmark(root: Path, start: str, end: str, fee: float) -> dict:
    left = pd.Timestamp(start, tz="UTC")
    right = pd.Timestamp(end, tz="UTC")
    if right <= left:
        raise ValueError("End must be after start")
    results = {}
    for asset in ("BTC", "ETH"):
        candles = load_candles(root, asset)
        window = candles.loc[(candles["date"] >= left) & (candles["date"] < right)]
        if len(window) < 2:
            raise RuntimeError(f"Insufficient {asset} candles for {start}–{end}")
        # Buy at the first window candle's open and sell at the final candle's
        # close. Apply fee to both legs; 100 USDT is the total entry expenditure.
        entry = float(window.iloc[0]["open"])
        exit_ = float(window.iloc[-1]["close"])
        if min(entry, exit_) <= 0:
            raise ValueError("Nonpositive market price")
        proceeds = 100.0 / (1.0 + fee) * (exit_ / entry) * (1.0 - fee)
        results[asset] = {
            "entry_utc": window.iloc[0]["date"].isoformat(),
            "exit_candle_utc": window.iloc[-1]["date"].isoformat(),
            "entry_open": entry,
            "exit_close": exit_,
            "profit_usdt": round(proceeds - 100.0, 4),
        }
    pnl = sum(v["profit_usdt"] for v in results.values())
    return {
        "start": start, "end_exclusive": end, "fee_per_side": fee,
        "initial_wallet_usdt": 10000, "capital_allocated_usdt": 200,
        "assets": results, "net_profit_usdt": round(pnl, 4),
        "wallet_return_pct": round(pnl / 10000 * 100, 5),
        "limitations": "No slippage/spread, intrabar fill simulation or rebalance; 2x100 USDT positions held throughout.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="user_data/data/coinbase")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--fee", type=float, default=0.012)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    if not 0 <= args.fee < 1:
        p.error("Fee must be between 0 and 1")
    result = benchmark(Path(args.data_dir), args.start, args.end, args.fee)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
