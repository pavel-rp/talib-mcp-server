from __future__ import annotations

from typing import List, Dict

import numpy as np
import talib  # type: ignore

__all__ = ["rsi", "macd", "ema", "sma", "bbands"]


def _to_list(arr: np.ndarray) -> List[float | None]:
    return [None if np.isnan(v) else float(v) for v in arr]


def _validate_prices(prices: List[float]):
    if not isinstance(prices, list) or not prices:
        raise ValueError("'prices' must be a non-empty list")
    if not all(isinstance(p, (int, float)) for p in prices):
        raise ValueError("All price values must be numeric")


def _validate_positive(value, name="value"):
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _validate_period(period: int, prices: List[float]):
    _validate_positive(period, "period")
    if period > len(prices):
        raise ValueError("period cannot exceed length of prices")


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------


def rsi(prices: List[float], period: int = 14) -> List[float | None]:
    _validate_prices(prices)
    _validate_period(period, prices)
    res = talib.RSI(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(res)


def macd(
    prices: List[float],
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> Dict[str, List[float | None]]:
    _validate_prices(prices)
    for p in (fastperiod, slowperiod, signalperiod):
        _validate_positive(p, "period parameter")
    macd_arr, signal_arr, hist_arr = talib.MACD(
        np.array(prices, dtype=float),
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod,
    )
    return {
        "macd": _to_list(macd_arr),
        "signal": _to_list(signal_arr),
        "hist": _to_list(hist_arr),
    }


def ema(prices: List[float], period: int = 10) -> List[float | None]:
    _validate_prices(prices)
    _validate_period(period, prices)
    res = talib.EMA(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(res)


def sma(prices: List[float], period: int = 10) -> List[float | None]:
    _validate_prices(prices)
    _validate_period(period, prices)
    res = talib.SMA(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(res)


def bbands(
    prices: List[float],
    period: int = 20,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
) -> Dict[str, List[float | None]]:
    _validate_prices(prices)
    _validate_period(period, prices)
    _validate_positive(nbdevup, "nbdevup")
    _validate_positive(nbdevdn, "nbdevdn")
    upper, middle, lower = talib.BBANDS(
        np.array(prices, dtype=float),
        timeperiod=period,
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
    )
    return {
        "upper": _to_list(upper),
        "middle": _to_list(middle),
        "lower": _to_list(lower),
    }