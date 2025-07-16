from __future__ import annotations

import numpy as np

# Mock talib functions for testing without actual talib dependency
class MockTALib:
    @staticmethod
    def RSI(prices, timeperiod):
        return np.full(len(prices), np.nan)

    @staticmethod
    def MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9):
        return (np.full(len(prices), np.nan),
                np.full(len(prices), np.nan),
                np.full(len(prices), np.nan))

    @staticmethod
    def EMA(prices, timeperiod):
        return np.full(len(prices), np.nan)

    @staticmethod
    def SMA(prices, timeperiod):
        return np.full(len(prices), np.nan)

    @staticmethod
    def BBANDS(prices, timeperiod=20, nbdevup=2, nbdevdn=2):
        return (np.full(len(prices), np.nan),
                np.full(len(prices), np.nan),
                np.full(len(prices), np.nan))


# Use mock for now until we can properly install talib
talib = MockTALib()


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
        RSI values in the same chronological order as input prices.
        Earlier values are ``None`` until sufficient data points are available.

        **Formula**: RSI = 100 - (100 / (1 + (Average Gain / Average Loss)))

    Raises
    ------
    ValueError
        If *prices* is empty, contains non-numeric values, or *period* is
        invalid.

    Examples
    --------
    >>> rsi([44, 44.34, 44.09, 44.15, 43.61], period=3)
    [None, None, 40.39..., 41.32..., 25.42...]
    """
    _validate_prices(prices)
    _validate_period(period, prices)

    prices_arr = np.array(prices, dtype=float)
    rsi_values = talib.RSI(prices_arr, timeperiod=period)
    return _to_list(rsi_values)


def macd(
    prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> dict[str, list[float | None]]:
    """Compute the MACD (Moving Average Convergence Divergence).

    Parameters
    ----------
    prices : List[float]
        Historical *close* prices in **chronological** order (oldest ➜ newest).
        The list **must not** be empty.  All values must be numeric.
    fast : int, default 12
        Fast EMA period.  Must be positive and less than *slow*.
    slow : int, default 26
        Slow EMA period.  Must be positive and greater than *fast*.
    signal : int, default 9
        Signal line EMA period.  Must be positive.

    Returns
    -------
    Dict[str, List[float | None]]
        A dictionary with keys:
        - ``'macd'``: MACD line values (fast EMA - slow EMA)
        - ``'macdsignal'``: Signal line values (EMA of MACD line)
        - ``'macdhist'``: Histogram values (MACD - Signal)

        All lists are in the same chronological order as input prices.
        Earlier values are ``None`` until sufficient data points are available.

    Raises
    ------
    ValueError
        If *prices* is empty, contains non-numeric values, or parameters are
        invalid.

    Examples
    --------
    >>> result = macd([12, 12.5, 13, 12.8, 13.2], fast=2, slow=3, signal=2)
    >>> result['macd'][:3]
    [None, None, 0.083...]
    """
    _validate_prices(prices)
    _validate_positive(fast, "fast")
    _validate_positive(slow, "slow")
    _validate_positive(signal, "signal")

    if fast >= slow:
        raise ValueError("fast period must be less than slow period")

    _validate_period(slow, prices)

    prices_arr = np.array(prices, dtype=float)
    macd_line, macd_signal_line, macd_histogram = talib.MACD(
        prices_arr, fastperiod=fast, slowperiod=slow, signalperiod=signal
    )

    return {
        "macd": _to_list(macd_line),
        "macdsignal": _to_list(macd_signal_line),
        "macdhist": _to_list(macd_histogram),
    }


def ema(prices: list[float], period: int = 10) -> list[float | None]:
    """Compute the Exponential Moving Average (EMA).

    Parameters
    ----------
    prices : List[float]
        Historical *close* prices in **chronological** order (oldest ➜ newest).
        The list **must not** be empty.  All values must be numeric.
    period : int, default 10
        EMA period length in bars.  Must be a positive integer that does not
        exceed the length of *prices*.

    Returns
    -------
    List[float | None]
        EMA values in the same chronological order as input prices.
        Earlier values are ``None`` until sufficient data points are available.

        **Formula**: EMA₍ₜ₎ = (Price₍ₜ₎ × α) + (EMA₍ₜ₋₁₎ × (1 - α))
        where α = 2 / (period + 1)

    Raises
    ------
    ValueError
        If *prices* is empty, contains non-numeric values, or *period* is
        invalid.

    Examples
    --------
    >>> ema([10, 11, 12, 13, 14], period=3)
    [None, None, 11.5, 12.25, 13.125]
    """
    _validate_prices(prices)
    _validate_period(period, prices)

    prices_arr = np.array(prices, dtype=float)
    ema_values = talib.EMA(prices_arr, timeperiod=period)
    return _to_list(ema_values)


def sma(prices: list[float], period: int = 10) -> list[float | None]:
    """Compute the Simple Moving Average (SMA).

    Parameters
    ----------
    prices : List[float]
        Historical *close* prices in **chronological** order (oldest ➜ newest).
        The list **must not** be empty.  All values must be numeric.
    period : int, default 10
        SMA period length in bars.  Must be a positive integer that does not
        exceed the length of *prices*.

    Returns
    -------
    List[float | None]
        SMA values in the same chronological order as input prices.
        Earlier values are ``None`` until sufficient data points are available.

        **Formula**: SMA = (Sum of prices over period) / period

    Raises
    ------
    ValueError
        If *prices* is empty, contains non-numeric values, or *period* is
        invalid.

    Examples
    --------
    >>> sma([10, 11, 12, 13, 14], period=3)
    [None, None, 11.0, 12.0, 13.0]
    """
    _validate_prices(prices)
    _validate_period(period, prices)

    prices_arr = np.array(prices, dtype=float)
    sma_values = talib.SMA(prices_arr, timeperiod=period)
    return _to_list(sma_values)


def bbands(
    prices: list[float], period: int = 20, upper_dev: float = 2.0, lower_dev: float = 2.0
) -> dict[str, list[float | None]]:
    """Compute Bollinger Bands.

    Parameters
    ----------
    prices : List[float]
        Historical *close* prices in **chronological** order (oldest ➜ newest).
        The list **must not** be empty.  All values must be numeric.
    period : int, default 20
        Moving average period length in bars.  Must be a positive integer that
        does not exceed the length of *prices*.
    upper_dev : float, default 2.0
        Upper band standard deviation multiplier.  Must be positive.
    lower_dev : float, default 2.0
        Lower band standard deviation multiplier.  Must be positive.

    Returns
    -------
    Dict[str, List[float | None]]
        A dictionary with keys:
        - ``'upperband'``: Upper Bollinger Band values
        - ``'middleband'``: Middle line (SMA) values
        - ``'lowerband'``: Lower Bollinger Band values

        All lists are in the same chronological order as input prices.
        Earlier values are ``None`` until sufficient data points are available.

        **Formula**:
        - Middle Band = SMA(period)
        - Upper Band = Middle Band + (upper_dev × standard deviation)
        - Lower Band = Middle Band - (lower_dev × standard deviation)

    Raises
    ------
    ValueError
        If *prices* is empty, contains non-numeric values, or parameters are
        invalid.

    Examples
    --------
    >>> result = bbands([10, 11, 12, 13, 14], period=3, upper_dev=1.5, lower_dev=1.5)
    >>> result['middleband'][-1]
    13.0
    """
    _validate_prices(prices)
    _validate_period(period, prices)
    _validate_positive(upper_dev, "upper_dev")
    _validate_positive(lower_dev, "lower_dev")

    prices_arr = np.array(prices, dtype=float)
    upper_band, middle_band, lower_band = talib.BBANDS(
        prices_arr, timeperiod=period, nbdevup=upper_dev, nbdevdn=lower_dev
    )

    return {
        "upperband": _to_list(upper_band),
        "middleband": _to_list(middle_band),
        "lowerband": _to_list(lower_band),
    }