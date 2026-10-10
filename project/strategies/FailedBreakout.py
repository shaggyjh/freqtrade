"""Research-only 4h false-breakout reversal, spot long only."""
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class FailedBreakout(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "6h"
    can_short = False
    minimal_roi = {"0": 0.08}
    stoploss = -0.06
    startup_candle_count = 110

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["prior_low"] = dataframe["low"].rolling(30).min().shift(1)
        dataframe["ema100"] = ta.EMA(dataframe, timeperiod=100)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Price dips below previous 30-bar low, then closes back above it.
        dataframe.loc[(dataframe["low"] < dataframe["prior_low"]) &
                      (dataframe["close"] > dataframe["prior_low"]) &
                      (dataframe["close"] > dataframe["open"]) &
                      ((dataframe["high"] - dataframe["low"]) > dataframe["atr"]) &
                      (dataframe["volume"] > 0), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["close"] < dataframe["ema100"]) &
                      (dataframe["volume"] > 0), "exit_long"] = 1
        return dataframe
