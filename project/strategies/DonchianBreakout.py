"""Research-only 4h breakout. Uses prior completed bars for thresholds."""
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class DonchianBreakout(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "6h"
    can_short = False
    minimal_roi = {"0": 0.20}
    stoploss = -0.10
    startup_candle_count = 110

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["high_lookback"] = dataframe["high"].rolling(55).max().shift(1)
        dataframe["low_exit"] = dataframe["low"].rolling(20).min().shift(1)
        dataframe["ema100"] = ta.EMA(dataframe, timeperiod=100)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["close"] > dataframe["high_lookback"]) &
                      (dataframe["close"] > dataframe["ema100"]) &
                      (dataframe["volume"] > 0), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["close"] < dataframe["low_exit"]) &
                      (dataframe["volume"] > 0), "exit_long"] = 1
        return dataframe
