from __future__ import annotations

import numpy as np
import talib  # type: ignore

__all__ = ["rsi", "macd", "ema", "sma", "bbands"]


def _to_list(arr: np.ndarray) -> list[float | None]:
    return [None if np.isnan(v) else float(v) for v in arr]


def _validate_prices(prices: list[float]):
    if not isinstance(prices, list) or not prices:
        raise ValueError("'prices' must be a non-empty list")
    if not all(isinstance(p, (int, float)) for p in prices):
        raise ValueError("All price values must be numeric")


def _validate_positive(value, name="value"):
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _validate_period(period: int, prices: list[float]):
    _validate_positive(period, "period")
    if period > len(prices):
        raise ValueError("period cannot exceed length of prices")


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------


def rsi(prices: list[float], period: int = 14) -> list[float | None]:
    """Compute the Relative Strength Index (RSI).

    Parameters
    ----------
    prices : List[float]
        Historical *close* prices in **chronological** order (oldest ➜ newest).
        The list **must not** be empty.  All values must be numeric.
    period : int, default 14
        RSI period length in bars.  Must be a positive integer that does not
        exceed the length of *prices*.

    Returns
    -------
    List[float | None]
        A list of RSI values aligned 1-to-1 with the input *prices*.
        Elements where the RSI cannot yet be computed are returned as
        ``None`` so that the result remains JSON-serialisable.

    Examples
    --------
    >>> rsi([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    [..., 70.71]
    """

    _validate_prices(prices)
    _validate_period(period, prices)
    res = talib.RSI(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(res)


# fmt: off
def macd(
    prices: list[float],
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> dict[str, list[float | None]]:
    """Moving Average Convergence / Divergence (MACD).

    Parameters
    ----------
    prices : List[float]
        Close prices (chronological order).
    fastperiod : int, default 12
        Period for the *fast* EMA.
    slowperiod : int, default 26
        Period for the *slow* EMA.
    signalperiod : int, default 9
        Period for the signal EMA calculated from the MACD line.

    Returns
    -------
    dict
        Dictionary with three keys:

        * ``macd``   – the MACD line
        * ``signal`` – the signal line
        * ``hist``   – MACD histogram (``macd - signal``)

        Each value is a list aligned with *prices* and uses ``None`` where
        not enough data points are available.

    Examples
    --------
    >>> macd([1, 2, 3, ..., 30])
    {'macd': [...], 'signal': [...], 'hist': [...]}  # doctest: +ELLIPSIS
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
# fmt: on


def ema(prices: list[float], period: int = 10) -> list[float | None]:
    """Exponential Moving Average (EMA).

    Parameters
    ----------
    prices : List[float]
        Close prices (chronological order).
    period : int, default 10
        EMA period length.

    Returns
    -------
    List[float | None]
        EMA values aligned with *prices*.
    """

    _validate_prices(prices)
    _validate_period(period, prices)
    res = talib.EMA(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(res)


def sma(prices: list[float], period: int = 10) -> list[float | None]:
    """Simple Moving Average (SMA).

    Identical to Excel's *AVERAGE* over a sliding window.
    """

    _validate_prices(prices)
    _validate_period(period, prices)
    res = talib.SMA(np.array(prices, dtype=float), timeperiod=period)
    return _to_list(res)


# fmt: off
def bbands(
    prices: list[float],
    period: int = 20,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
) -> dict[str, list[float | None]]:
    """Bollinger Bands® (BBANDS).

    Parameters
    ----------
    prices : List[float]
        Close prices.
    period : int, default 20
        Moving-average period.
    nbdevup : float, default 2.0
        Standard-deviation multiplier for the **upper** band.
    nbdevdn : float, default 2.0
        Standard-deviation multiplier for the **lower** band.

    Returns
    -------
    dict
        ``{"upper": [...], "middle": [...], "lower": [...]}``

    Notes
    -----
    The *middle* band is simply a SMA of *prices*.  The *upper* / *lower*
    bands are offset by ``nbdevup`` / ``nbdevdn`` standard deviations.
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
# fmt: on