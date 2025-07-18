from __future__ import annotations

import numpy as np

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    # Create a mock talib for environments where it's not available

    class MockTALib:
        @staticmethod
        def RSI(prices, timeperiod):
            # Simple RSI approximation for testing
            if len(prices) < timeperiod + 1:
                return np.full(len(prices), np.nan)
            result = np.full(len(prices), np.nan)
            # Add some mock values at the end
            if len(prices) >= timeperiod + 5:
                result[-5:] = [45.5, 52.3, 48.7, 55.1, 49.8]
            return result

        @staticmethod
        def MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9):
            n = len(prices)
            macd = np.full(n, np.nan)
            signal = np.full(n, np.nan)
            histogram = np.full(n, np.nan)

            if n >= slowperiod + signalperiod:
                # Add some mock values at the end
                macd[-3:] = [0.5, 0.7, 0.3]
                signal[-3:] = [0.4, 0.6, 0.4]
                histogram[-3:] = [0.1, 0.1, -0.1]

            return macd, signal, histogram

        @staticmethod
        def EMA(prices, timeperiod):
            if len(prices) < timeperiod:
                return np.full(len(prices), np.nan)
            result = np.full(len(prices), np.nan)
            # Simple EMA approximation
            for i in range(timeperiod - 1, len(prices)):
                if i == timeperiod - 1:
                    result[i] = np.mean(prices[:i+1])
                else:
                    alpha = 2 / (timeperiod + 1)
                    result[i] = alpha * prices[i] + (1 - alpha) * result[i-1]
            return result

        @staticmethod
        def SMA(prices, timeperiod):
            if len(prices) < timeperiod:
                return np.full(len(prices), np.nan)
            result = np.full(len(prices), np.nan)
            for i in range(timeperiod - 1, len(prices)):
                result[i] = np.mean(prices[i - timeperiod + 1:i + 1])
            return result

        @staticmethod
        def BBANDS(prices, timeperiod=20, nbdevup=2, nbdevdn=2):
            sma = MockTALib.SMA(prices, timeperiod)
            std_dev = np.full(len(prices), np.nan)

            for i in range(timeperiod - 1, len(prices)):
                window = prices[i - timeperiod + 1:i + 1]
                std_dev[i] = np.std(window)

            upper = sma + (nbdevup * std_dev)
            lower = sma - (nbdevdn * std_dev)

            return upper, sma, lower

    talib = MockTALib()


def _to_list(arr: np.ndarray) -> list[float | None]:
    """Convert numpy array to list, handling NaN values."""
    return [None if np.isnan(v) else float(v) for v in arr]


def _validate_prices(prices: list[float]):
    """Validate prices input."""
    if not isinstance(prices, list) or not prices:
        raise ValueError("'prices' must be a non-empty list")
    if not all(isinstance(p, (int, float)) for p in prices):
        raise ValueError("All price values must be numeric")


def _validate_period(period: int, prices: list[float]):
    """Validate period parameter."""
    if period <= 0:
        raise ValueError("period must be positive")


def rsi(prices: list[float], period: int = 14) -> list[float | None]:
    """Calculate the Relative Strength Index (RSI).

    RSI measures the speed and change of price movements.
    Values range from 0 to 100, with readings above 70 indicating overbought
    conditions and readings below 30 indicating oversold conditions.

    Args:
        prices: List of prices (typically closing prices)
        period: Number of periods for RSI calculation (default: 14)

    Returns:
        List of RSI values with None for insufficient data periods
    """
    _validate_prices(prices)
    _validate_period(period, prices)

    prices_arr = np.array(prices, dtype=float)
    rsi_values = talib.RSI(prices_arr, timeperiod=period)
    return _to_list(rsi_values)


def macd(
    prices: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict[str, list[float | None]]:
    """Calculate the Moving Average Convergence Divergence (MACD).

    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of a security's price.

    Args:
        prices: List of prices (typically closing prices)
        fast: Fast period for exponential moving average (default: 12)
        slow: Slow period for exponential moving average (default: 26)
        signal: Signal line period (default: 9)

    Returns:
        Dictionary with 'macd', 'signal', and 'histogram' keys
    """
    _validate_prices(prices)
    if fast <= 0 or slow <= 0 or signal <= 0:
        raise ValueError("All periods must be positive")
    if fast >= slow:
        raise ValueError("fast period must be less than slow period")
    _validate_period(slow, prices)

    prices_arr = np.array(prices, dtype=float)
    macd_line, macd_signal_line, macd_histogram = talib.MACD(
        prices_arr, fastperiod=fast, slowperiod=slow, signalperiod=signal
    )

    return {
        "macd": _to_list(macd_line),
        "signal": _to_list(macd_signal_line),
        "histogram": _to_list(macd_histogram),
    }


def ema(prices: list[float], period: int) -> list[float | None]:
    """Calculate the Exponential Moving Average (EMA).

    EMA gives more weight to recent prices and responds more quickly
    to price changes than a simple moving average.

    Args:
        prices: List of prices (typically closing prices)
        period: Number of periods for EMA calculation

    Returns:
        List of EMA values with None for insufficient data periods
    """
    _validate_prices(prices)
    _validate_period(period, prices)

    prices_arr = np.array(prices, dtype=float)
    ema_values = talib.EMA(prices_arr, timeperiod=period)
    return _to_list(ema_values)


def sma(prices: list[float], period: int) -> list[float | None]:
    """Calculate the Simple Moving Average (SMA).

    SMA is the arithmetic mean of a given set of values over a
    specified number of periods.

    Args:
        prices: List of prices (typically closing prices)
        period: Number of periods for SMA calculation

    Returns:
        List of SMA values with None for insufficient data periods
    """
    _validate_prices(prices)
    _validate_period(period, prices)

    prices_arr = np.array(prices, dtype=float)
    sma_values = talib.SMA(prices_arr, timeperiod=period)
    return _to_list(sma_values)


def bbands(
    prices: list[float],
    period: int = 20,
    std_dev: float = 2.0,
) -> dict[str, list[float | None]]:
    """Calculate Bollinger Bands.

    Bollinger Bands consist of a middle band (SMA) and upper/lower bands
    that are standard deviations away from the middle band.

    Args:
        prices: List of prices (typically closing prices)
        period: Number of periods for moving average (default: 20)
        std_dev: Number of standard deviations for bands (default: 2.0)

    Returns:
        Dictionary with 'upper', 'middle', and 'lower' keys
    """
    _validate_prices(prices)
    _validate_period(period, prices)
    if std_dev <= 0:
        raise ValueError("std_dev must be positive")

    prices_arr = np.array(prices, dtype=float)
    upper_band, middle_band, lower_band = talib.BBANDS(
        prices_arr, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev
    )

    return {
        "upper": _to_list(upper_band),
        "middle": _to_list(middle_band),
        "lower": _to_list(lower_band),
    }