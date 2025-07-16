from __future__ import annotations

"""TA-Lib indicator wrapper functions exposed as MCP tools.

All functions are **stateless** and return plain Python data structures
that are automatically serialisable by FastMCP.  Each tool validates its
inputs and raises a `ValueError` for invalid arguments so that FastMCP
can convert them into a `400` response.
"""

from typing import List, Dict

import numpy as np
import talib  # type: ignore

__all__ = [
    "rsi",
    "macd",
    "ema",
    "sma",
    "bbands",
]


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _to_list(array: np.ndarray) -> List[float | None]:
    """Convert a numpy array into a list while replacing *nan* with ``None``."""

    return [None if np.isnan(x) else float(x) for x in array]


# ---------------------------------------------------------------------------
# Indicator implementations
# ---------------------------------------------------------------------------

def rsi(prices: List[float], period: int = 14) -> List[float | None]:
    """Relative Strength Index (RSI).

    Parameters
    ----------
    prices:
        List of *close* prices in chronological order (oldest first).
    period:
        RSI period length.  Must be positive and less than or equal to the
        length of *prices*.

    Returns
    -------
    List[float | None]
        A list of RSI values aligned 1-to-1 with *prices*.  Elements that
        cannot be computed are returned as ``None`` to remain JSON serialisable.
    """

    _validate_prices(prices)
    _validate_period(period, prices)

    result = talib.RSI(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(result)


def macd(
    prices: List[float],
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> Dict[str, List[float | None]]:
    """Moving Average Convergence/Divergence (MACD).

    Parameters
    ----------
    prices:
        List of *close* prices in chronological order (oldest first).
    fastperiod:
        Fast EMA period.
    slowperiod:
        Slow EMA period.
    signalperiod:
        Signal EMA period.

    Returns
    -------
    dict[str, List[float | None]]
        Dictionary containing keys ``macd``, ``signal``, ``hist`` where each
        value is a list aligned with *prices*.
    """

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
    """Exponential Moving Average (EMA)."""

    _validate_prices(prices)
    _validate_period(period, prices)

    result = talib.EMA(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(result)


def sma(prices: List[float], period: int = 10) -> List[float | None]:
    """Simple Moving Average (SMA)."""

    _validate_prices(prices)
    _validate_period(period, prices)

    result = talib.SMA(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(result)


def bbands(
    prices: List[float],
    period: int = 20,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
) -> Dict[str, List[float | None]]:
    """Bollinger Bands (BBANDS).

    Returns *upper*, *middle*, and *lower* bands as separate lists.
    """

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


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_prices(prices: List[float]) -> None:
    if not isinstance(prices, list):
        raise ValueError("'prices' must be a list of floats")
    if not prices:
        raise ValueError("'prices' list must not be empty")
    if not all(isinstance(p, (int, float)) for p in prices):
        raise ValueError("All items in 'prices' must be numeric (int | float)")


def _validate_period(period: int, prices: List[float]) -> None:
    _validate_positive(period, "period")
    if period > len(prices):
        raise ValueError("'period' cannot be greater than length of 'prices'")


def _validate_positive(value: float | int, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")