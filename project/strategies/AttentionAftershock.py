from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class AttentionAftershock(IStrategy):
    """OHLCV-only proxy for attention saturation, NOT measured public attention.

    Hypothesis: an unusual volume/price shock attracts reactive participants.
    After activity fades, a stable price and renewed upward momentum may indicate
    that forced/reactive selling has been absorbed. Long-only, next-candle signals.
    """
    INTERFACE_VERSION = 3
    timeframe = "6h"
    can_short = False
    startup_candle_count = 100
    minimal_roi = {"0": 0.04}
    stoploss = -0.08
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["vol_median"] = dataframe["volume"].rolling(40).median().shift(1)
        dataframe["shock"] = (
            (dataframe["volume"] > 2.0 * dataframe["vol_median"])
            & ((dataframe["high"] - dataframe["low"]) / dataframe["close"] > 0.025)
        )
        # The shock must have occurred at least two CLOSED candles ago.
        dataframe["recent_shock"] = (
            dataframe["shock"].shift(2).fillna(False)
            | dataframe["shock"].shift(3).fillna(False)
            | dataframe["shock"].shift(4).fillna(False)
        )
        dataframe["quiet"] = dataframe["volume"] < dataframe["vol_median"] * 1.1
        dataframe["recovery"] = (dataframe["close"] > dataframe["open"]) & (
            dataframe["close"] > dataframe["close"].shift(1)
        )
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            dataframe["recent_shock"]
            & dataframe["quiet"]
            & dataframe["recovery"]
            & (dataframe["close"] > dataframe["ema50"])
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["ema50"]) & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
