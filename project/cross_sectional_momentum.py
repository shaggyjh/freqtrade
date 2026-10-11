"""Research-only cross-sectional momentum allocation, no orders or live trading.

Daily decisions from completed UTC 1d closes, executed at the next daily open.
Fixed universe is configured by downloaded Coinbase candles; unavailable pairs
are excluded explicitly and must be reported (not silently substituted).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

def load_daily(root: Path, symbol: str) -> pd.DataFrame:
    files = sorted(root.rglob(f"{symbol}_USDT-1d.feather"))
    if len(files) != 1:
        raise FileNotFoundError(f"Expected one {symbol} daily feather file, found {len(files)}")
    frame = pd.read_feather(files[0])
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    return frame.sort_values("date")


UNIVERSE = ("BTC", "ETH", "SOL", "XRP", "ADA", "LINK", "LTC", "DOGE")
LOOKBACK = 30
VOL_WINDOW = 30
HOLDINGS = 3
REBALANCE_DAYS = 7
START_CAPITAL = 10000.0


def evaluate(root: Path, fee: float) -> dict:
    prices = {}
    missing = {}
    for symbol in UNIVERSE:
        try:
            df = load_daily(root, symbol)[["date", "open", "close"]].copy()
            if df.empty:
                raise ValueError("empty")
            df = df.set_index("date").sort_index()
            prices[symbol] = df
        except (FileNotFoundError, ValueError, KeyError) as exc:
            missing[symbol] = str(exc)
    if len(prices) < 4:
        raise ValueError(f"At least four assets needed; missing: {missing}")
    # Strict common calendar: no stale-price forward filling.
    dates = sorted(set.intersection(*(set(df.index) for df in prices.values())))
    if len(dates) < 100:
        raise ValueError("Insufficient overlapping daily history")
    opens = pd.DataFrame({s: df.loc[dates, "open"] for s, df in prices.items()}, index=dates)
    closes = pd.DataFrame({s: df.loc[dates, "close"] for s, df in prices.items()}, index=dates)
    if (opens <= 0).any().any() or (closes <= 0).any().any():
        raise ValueError("Nonpositive price")
    if (pd.Series(dates).diff().dropna() != pd.Timedelta(days=1)).any():
        raise ValueError("Daily calendar has gaps")
    returns = closes.pct_change()
    # At close i, select using closes through i; trade at next open i+1.
    # Rebalance every 7 days. Mark holdings open-to-open to avoid lookahead.
    cash = START_CAPITAL
    units = {s: 0.0 for s in prices}
    turnover = 0.0
    rebalances = 0
    trades = 0
    equity_curve = []
    for i in range(LOOKBACK + 1, len(dates)):
        px = opens.iloc[i]
        equity = cash + sum(units[s] * px[s] for s in units)
        equity_curve.append(equity)
        if (i - (LOOKBACK + 1)) % REBALANCE_DAYS != 0:
            continue
        signal_i = i - 1
        momentum = closes.iloc[signal_i] / closes.iloc[signal_i - LOOKBACK] - 1
        volatility = returns.iloc[signal_i - VOL_WINDOW + 1:signal_i + 1].std()
        # BTC trend gate based solely on known previous close and prior 30d close.
        market_ok = "BTC" in closes and momentum["BTC"] > 0
        score = (momentum / volatility.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
        eligible = score[(momentum > 0) & score.notna()].sort_values(ascending=False)
        chosen = list(eligible.head(HOLDINGS).index) if market_ok else []
        target = {s: (1.0 / len(chosen) if s in chosen else 0.0) for s in units}
        # Sell first; fees deducted in quote currency.
        for s in units:
            current = units[s] * px[s]
            desired = equity * target[s]
            if current > desired + 0.01:
                gross = current - desired
                quantity = gross / px[s]
                units[s] -= quantity
                cash += gross * (1 - fee)
                turnover += gross
                trades += 1
        # Recompute spendable cash; target holdings are capped by available cash.
        for s in chosen:
            desired = equity * target[s]
            current = units[s] * px[s]
            shortfall = max(0.0, desired - current)
            gross = min(shortfall, cash / (1 + fee))
            if gross > 0.01:
                units[s] += gross / px[s]
                cash -= gross * (1 + fee)
                turnover += gross
                trades += 1
        rebalances += 1
    final_px = closes.iloc[-1]
    final_equity = cash + sum(units[s] * final_px[s] * (1 - fee) for s in units)
    benchmark = {}
    for s in ("BTC", "ETH"):
        if s in prices:
            benchmark[s] = round(
                START_CAPITAL * (closes[s].iloc[-1] / opens[s].iloc[LOOKBACK + 1])
                * (1 - fee) / (1 + fee) - START_CAPITAL, 2
            )
    return {
        "research_only": True, "first_day": str(dates[LOOKBACK + 1]),
        "last_day": str(dates[-1]), "assets_used": list(prices),
        "missing_assets": missing, "fee_per_side": fee,
        "rebalance_days": REBALANCE_DAYS, "rebalances": rebalances,
        "order_count": trades, "gross_turnover_usdt": round(turnover, 2),
        "starting_capital_usdt": START_CAPITAL,
        "ending_equity_usdt": round(final_equity, 2),
        "net_profit_usdt": round(final_equity - START_CAPITAL, 2),
        "net_return_pct": round((final_equity / START_CAPITAL - 1) * 100, 3),
        "max_drawdown_pct_open_marks": round(
            (1 - min(np.array(equity_curve) / np.maximum.accumulate(equity_curve))) * 100, 3
        ),
        "full_capital_buy_hold_net_profit_usdt": benchmark,
        "limitations": "Research-only daily-open proxy; no spread, market impact, exchange minimum orders, delistings or survivorship correction. The preselected coin universe and observed history are not prospective validation. BTC/ETH hold comparators have different exposure. End liquidation fee estimated.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--fee", type=float, default=0.007)
    a = p.parse_args()
    if not 0 <= a.fee < 1:
        p.error("Invalid fee")
    result = evaluate(Path(a.data_dir), a.fee)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
