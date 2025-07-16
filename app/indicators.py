from __future__ import annotations

from hexital import RSI, MACD, EMA, SMA, BBANDS, Candle


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
    if len(prices) < period:
        return [None] * len(prices)
    
    # Convert prices to Candle objects (using price as OHLC since we only have close)
    candles = [Candle(open=price, high=price, low=price, close=price, volume=1000) 
               for price in prices]
    
    # Calculate RSI
    rsi_indicator = RSI(candles=candles, period=period)
    rsi_indicator.calculate()
    
    # Extract values
    result = []
    for candle in candles:
        rsi_value = getattr(candle, f'RSI_{period}', None)
        result.append(rsi_value if rsi_value is not None else None)
    
    return result


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
    if len(prices) < max(fast, slow):
        none_values = [None] * len(prices)
        return {
            "macd": none_values,
            "signal": none_values,
            "histogram": none_values,
        }
    
    # Convert prices to Candle objects
    candles = [Candle(open=price, high=price, low=price, close=price, volume=1000) 
               for price in prices]
    
    # Calculate MACD
    macd_indicator = MACD(candles=candles, fast=fast, slow=slow, signal=signal)
    macd_indicator.calculate()
    
    # Extract values
    macd_values = []
    signal_values = []
    histogram_values = []
    
    for candle in candles:
        macd_val = getattr(candle, f'MACD_{fast}_{slow}_{signal}', None)
        signal_val = getattr(candle, f'MACD_signal_{fast}_{slow}_{signal}', None)
        histogram_val = getattr(candle, f'MACD_histogram_{fast}_{slow}_{signal}', None)
        
        macd_values.append(macd_val if macd_val is not None else None)
        signal_values.append(signal_val if signal_val is not None else None)
        histogram_values.append(histogram_val if histogram_val is not None else None)
    
    return {
        "macd": macd_values,
        "signal": signal_values,
        "histogram": histogram_values,
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
    if len(prices) < period:
        return [None] * len(prices)
    
    # Convert prices to Candle objects
    candles = [Candle(open=price, high=price, low=price, close=price, volume=1000) 
               for price in prices]
    
    # Calculate EMA
    ema_indicator = EMA(candles=candles, period=period)
    ema_indicator.calculate()
    
    # Extract values
    result = []
    for candle in candles:
        ema_value = getattr(candle, f'EMA_{period}', None)
        result.append(ema_value if ema_value is not None else None)
    
    return result


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
    if len(prices) < period:
        return [None] * len(prices)
    
    # Convert prices to Candle objects
    candles = [Candle(open=price, high=price, low=price, close=price, volume=1000) 
               for price in prices]
    
    # Calculate SMA
    sma_indicator = SMA(candles=candles, period=period)
    sma_indicator.calculate()
    
    # Extract values
    result = []
    for candle in candles:
        sma_value = getattr(candle, f'SMA_{period}', None)
        result.append(sma_value if sma_value is not None else None)
    
    return result


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
    if len(prices) < period:
        none_values = [None] * len(prices)
        return {
            "upper": none_values,
            "middle": none_values,
            "lower": none_values,
        }
    
    # Convert prices to Candle objects
    candles = [Candle(open=price, high=price, low=price, close=price, volume=1000) 
               for price in prices]
    
    # Calculate Bollinger Bands
    bb_indicator = BBANDS(candles=candles, period=period, std_dev=std_dev)
    bb_indicator.calculate()
    
    # Extract values
    upper_values = []
    middle_values = []
    lower_values = []
    
    for candle in candles:
        upper_val = getattr(candle, f'BBANDS_upper_{period}_{std_dev}', None)
        middle_val = getattr(candle, f'BBANDS_middle_{period}_{std_dev}', None)
        lower_val = getattr(candle, f'BBANDS_lower_{period}_{std_dev}', None)
        
        upper_values.append(upper_val if upper_val is not None else None)
        middle_values.append(middle_val if middle_val is not None else None)
        lower_values.append(lower_val if lower_val is not None else None)
    
    return {
        "upper": upper_values,
        "middle": middle_values,
        "lower": lower_values,
    }