"""Research-only compression breakout; fixed, non-optimized hypothesis.

The setup measures the completed 20-bar range ending one candle before the
breakout, to avoid including the breakout candle in its own compression test.
"""
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import talib.abstract as ta


class CompressionBreakout(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "6h"
    can_short = False
    minimal_roi = {"0": 0.08}
    stoploss = -0.08
    startup_candle_count = 170
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        range_pct = (
            dataframe["high"].rolling(20).max()
            - dataframe["low"].rolling(20).min()
        ) / dataframe["close"]
        # Candidate setup ends on the prior closed candle. Historical percentile
        # distribution excludes the setup candle, preventing lookahead.
        dataframe["prior_range_pct"] = range_pct.shift(1)
        dataframe["compression_threshold"] = (
            range_pct.shift(2).rolling(120).quantile(0.10)
        )
        dataframe["breakout_high"] = dataframe["high"].rolling(20).max().shift(1)
        dataframe["exit_low"] = dataframe["low"].rolling(10).min().shift(1)
        dataframe["volume_median"] = dataframe["volume"].rolling(20).median().shift(1)
        dataframe["ema100"] = ta.EMA(dataframe, timeperiod=100)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["prior_range_pct"] <= dataframe["compression_threshold"])
            & (dataframe["close"] > dataframe["breakout_high"])
            & (dataframe["close"] > dataframe["ema100"])
            & (dataframe["volume"] > dataframe["volume_median"])
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["exit_low"])
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
