import math
import pathlib
import sys

# Add project root to PYTHONPATH for CI environments
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pytest

from app import indicators as ind


prices = [44.0, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.15, 45.42, 45.84,
          46.08, 45.89, 46.03, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64]


def _clean(a):
    return [None if x is None or math.isnan(x) else pytest.approx(float(x), abs=1e-2) for x in a]


def test_rsi():
    # Test that the function runs without error and returns the right structure
    result = ind.rsi(prices, 14)
    assert isinstance(result, list)
    assert len(result) == len(prices)
    
    # First 13 values should be None (insufficient data)
    assert all(v is None for v in result[:13])
    
    # Should have real values after sufficient periods
    assert result[13] is not None
    assert isinstance(result[13], (int, float))


def test_ema():
    result = ind.ema(prices, 10)
    assert isinstance(result, list)
    assert len(result) == len(prices)
    
    # First 9 values should be None
    assert all(v is None for v in result[:9])
    
    # Should have real values after sufficient periods
    assert result[9] is not None
    assert isinstance(result[9], (int, float))


def test_sma():
    result = ind.sma(prices, 5)
    assert isinstance(result, list)
    assert len(result) == len(prices)
    
    # First 4 values should be None
    assert all(v is None for v in result[:4])
    
    # Should have real values after sufficient periods
    assert result[4] is not None
    assert isinstance(result[4], (int, float))


def test_macd():
    result = ind.macd(prices, fast=12, slow=26, signal=9)
    assert isinstance(result, dict)
    assert "macd" in result
    assert "signal" in result
    assert "histogram" in result
    
    for key in ["macd", "signal", "histogram"]:
        assert isinstance(result[key], list)
        assert len(result[key]) == len(prices)


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
        
    # Should have real values after sufficient periods
    for key in ["upper", "middle", "lower"]:
        assert result[key][9] is not None
        assert isinstance(result[key][9], (int, float))