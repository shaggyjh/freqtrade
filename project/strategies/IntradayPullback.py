"""Experimental 15m intraday trend pullback; spot-only, no leverage."""
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import talib.abstract as ta


class IntradayPullback(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "15m"
    can_short = False
    minimal_roi = {"0": 0.025, "120": 0.012, "360": 0.0}
    stoploss = -0.018
    startup_candle_count = 80

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema20"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["volume_mean"] = dataframe["volume"].rolling(20).mean().shift(1)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Prior bar below EMA20, current bar reclaims it in an uptrend.
        dataframe.loc[
            (dataframe["ema20"] > dataframe["ema50"])
            & (dataframe["close"].shift(1) < dataframe["ema20"].shift(1))
            & (dataframe["close"] > dataframe["ema20"])
            & (dataframe["rsi"] > 48)
            & (dataframe["rsi"] < 70)
            & (dataframe["volume"] > dataframe["volume_mean"] * 0.7)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            ((dataframe["close"] < dataframe["ema50"]) | (dataframe["rsi"] > 76))
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
