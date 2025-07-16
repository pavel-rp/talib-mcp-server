import math
import pathlib
import sys

# Add project root to PYTHONPATH for CI environments
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pytest

from app import indicators as ind


# Using realistic price data for testing - need more data points for TA-Lib
prices = [44.0, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.15, 45.42, 45.84,
          46.08, 45.89, 46.03, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64,
          45.89, 46.25, 46.23, 46.08, 46.03, 46.83, 46.69, 46.49, 46.26, 46.09,
          45.81, 45.68, 45.57, 45.56, 45.51, 45.02, 44.84, 44.69, 44.62, 44.60]


def _clean(a):
    """Clean list for comparison, handling None and NaN values."""
    return [None if x is None or (isinstance(x, float) and math.isnan(x))
            else pytest.approx(float(x), abs=1e-2) for x in a]


def test_rsi():
    # Test RSI calculation
    result = ind.rsi(prices, 14)
    assert isinstance(result, list)
    assert len(result) == len(prices)

    # First 13 values should be None (TA-Lib needs period values)
    assert all(v is None for v in result[:13])

    # Should have calculated values after period
    assert result[13] is not None
    assert isinstance(result[13], float)
    assert 0 <= result[13] <= 100  # RSI should be between 0 and 100


def test_ema():
    result = ind.ema(prices, 10)
    assert isinstance(result, list)
    assert len(result) == len(prices)

    # First 9 values should be None (TA-Lib needs period-1 values)
    assert all(v is None for v in result[:9])

    # Should have calculated values after warmup
    assert result[9] is not None
    assert isinstance(result[9], float)


def test_sma():
    result = ind.sma(prices, 5)
    assert isinstance(result, list)
    assert len(result) == len(prices)

    # First 4 values should be None
    assert all(v is None for v in result[:4])

    # Should have calculated values after period
    assert result[4] is not None
    assert isinstance(result[4], float)

    # Test known calculation - SMA of first 5 values
    expected_sma_5 = sum(prices[:5]) / 5
    assert abs(result[4] - expected_sma_5) < 1e-10


def test_macd():
    result = ind.macd(prices, fast=12, slow=26, signal=9)
    assert isinstance(result, dict)
    assert "macd" in result
    assert "signal" in result
    assert "histogram" in result

    for key in ["macd", "signal", "histogram"]:
        assert isinstance(result[key], list)
        assert len(result[key]) == len(prices)

    # MACD requires slow period before it starts calculating
    # So first 25 values should be None
    assert all(v is None for v in result["macd"][:25])


def test_bbands():
    result = ind.bbands(prices, period=10, std_dev=2.0)
    assert isinstance(result, dict)
    assert "upper" in result
    assert "middle" in result
    assert "lower" in result

    for key in ["upper", "middle", "lower"]:
        assert isinstance(result[key], list)
        assert len(result[key]) == len(prices)

    # First 9 values should be None
    for key in ["upper", "middle", "lower"]:
        assert all(v is None for v in result[key][:9])

    # After period, should have real values
    for key in ["upper", "middle", "lower"]:
        assert result[key][9] is not None
        assert isinstance(result[key][9], float)

    # Upper band should be above middle, lower band should be below
    assert result["upper"][9] > result["middle"][9]
    assert result["lower"][9] < result["middle"][9]


def test_input_validation():
    # Test empty prices
    with pytest.raises(ValueError, match="non-empty list"):
        ind.rsi([])

    # Test invalid period
    with pytest.raises(ValueError, match="positive"):
        ind.rsi(prices, 0)

    # Test non-numeric prices
    with pytest.raises(ValueError, match="numeric"):
        ind.rsi(["a", "b", "c"], 2)