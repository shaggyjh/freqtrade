"""Experimental behavioural proxy: high-volume downside capitulation followed by recovery.

OHLCV candles do not reveal investor identities, news attention, or order flow.
This is only a price/volume proxy, not a validated behavioural signal.
"""
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import talib.abstract as ta


class CrowdExhaustion(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "6h"
    can_short = False
    minimal_roi = {"0": 0.04}
    stoploss = -0.08
    startup_candle_count = 80
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["volume_median"] = dataframe["volume"].rolling(30).median().shift(1)
        dataframe["prior_low"] = dataframe["low"].rolling(20).min().shift(1)
        dataframe["ema_trend"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["range"] = (dataframe["high"] - dataframe["low"]).clip(lower=0.00000001)
        dataframe["lower_wick_share"] = (
            dataframe[["open", "close"]].min(axis=1) - dataframe["low"]
        ) / dataframe["range"]
        dataframe["capitulation"] = (
            (dataframe["low"] < dataframe["prior_low"])
            & (dataframe["volume"] > 2 * dataframe["volume_median"])
            & (dataframe["lower_wick_share"] > 0.5)
            & (dataframe["close"] > dataframe["open"])
        )
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            dataframe["capitulation"].shift(1).fillna(False)
            & (dataframe["close"] > dataframe["close"].shift(1))
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["ema_trend"])
            & (dataframe["close"].shift(1) >= dataframe["ema_trend"].shift(1))
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
