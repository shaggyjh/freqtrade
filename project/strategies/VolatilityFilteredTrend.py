"""Research hypothesis: avoid EMA crossover entries during unusually turbulent periods."""
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import talib.abstract as ta


class VolatilityFilteredTrend(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "6h"
    can_short = False
    minimal_roi = {"0": 0.04}
    stoploss = -0.08
    startup_candle_count = 100
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
        dataframe["atr_baseline"] = dataframe["atr_pct"].rolling(60).median().shift(1)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["ema_fast"] > dataframe["ema_slow"])
            & (dataframe["ema_fast"].shift(1) <= dataframe["ema_slow"].shift(1))
            & (dataframe["atr_pct"] < 1.5 * dataframe["atr_baseline"])
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["ema_fast"] < dataframe["ema_slow"])
            & (dataframe["ema_fast"].shift(1) >= dataframe["ema_slow"].shift(1))
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
