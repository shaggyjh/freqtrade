"""Exploratory BTC/ETH ratio event study; no orders and no trading P&L claim."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from benchmark_buy_hold import load_candles


def study(root: Path) -> dict:
    btc = load_candles(root, "BTC")[["date", "close"]].rename(columns={"close": "btc"})
    eth = load_candles(root, "ETH")[["date", "close"]].rename(columns={"close": "eth"})
    frame = btc.merge(eth, on="date", validate="one_to_one").sort_values("date")
    if len(frame) < 120 or (frame[["btc", "eth"]] <= 0).any().any():
        raise ValueError("Missing sufficient synchronized positive-price candles")
    if (frame["date"].diff().dropna() != pd.Timedelta(hours=6)).any():
        raise ValueError("Non-contiguous 6h candles; cannot trust event horizons")
    ratio = np.log(frame["eth"] / frame["btc"])
    prior_mean = ratio.shift(1).rolling(60).mean()
    prior_std = ratio.shift(1).rolling(60).std()
    z = (ratio - prior_mean) / prior_std.replace(0, np.nan)
    events = {}
    for side, sign in (("eth_rich", 1), ("eth_cheap", -1)):
        candidates = np.flatnonzero((z * sign > 2).fillna(False).to_numpy())
        selected = []
        previous = -29
        for index in candidates:
            if index - previous >= 28 and index + 29 < len(frame):
                selected.append(int(index))
                previous = index
        horizons = {}
        for horizon in (4, 12, 28):
            # Signal is at candle close; future relative move starts at next
            # candle open, never at the already-observed signal close.
            entry = np.log(
                frame["eth"].iloc[np.array(selected) + 1].to_numpy()
                / frame["btc"].iloc[np.array(selected) + 1].to_numpy()
            ) if selected else np.array([])
            exit_ = ratio.iloc[np.array(selected) + horizon].to_numpy() if selected else np.array([])
            changes = (exit_ - entry) * (-sign)
            horizons[str(horizon)] = {
                "n": len(selected),
                "mean_reversion_log_return": round(float(changes.mean()), 6) if len(changes) else None,
                "median_reversion_log_return": round(float(np.median(changes)), 6) if len(changes) else None,
            }
        events[side] = {
            "count": len(selected),
            "sufficient_events": len(selected) >= 30,
            "horizons_6h_candles": horizons,
        }
    return {
        "research_only": True,
        "first_candle": frame["date"].iloc[0].isoformat(),
        "last_candle": frame["date"].iloc[-1].isoformat(),
        "candles": len(frame),
        "event_study": events,
        "warning": "Relative log-ratio movement is NOT executable spot-only P&L. No hedged short leg, fees, slippage or funding modeled. Already-inspected sample is development only.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="user_data/data/coinbase")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = study(Path(args.data_dir))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
