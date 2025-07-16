import math

import numpy as np
import pytest
import talib

from app import indicators as ind

prices = list(range(1, 31))  # 1..30
prices_arr = np.array(prices, dtype=float)


def _clean(arr):
    """Convert numpy array to list with None for nan."""

    return [None if math.isnan(x) else pytest.approx(float(x)) for x in arr]


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------


def test_rsi_matches_talib():
    expected = _clean(talib.RSI(prices_arr, timeperiod=14))
    result = ind.rsi(prices, 14)
    assert result == expected


# ---------------------------------------------------------------------------
# EMA / SMA
# ---------------------------------------------------------------------------


def test_ema_matches_talib():
    expected = _clean(talib.EMA(prices_arr, timeperiod=10))
    assert ind.ema(prices, 10) == expected


def test_sma_matches_talib():
    expected = _clean(talib.SMA(prices_arr, timeperiod=10))
    assert ind.sma(prices, 10) == expected


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------


def test_macd_matches_talib():
    macd_arr, signal_arr, hist_arr = talib.MACD(prices_arr, 12, 26, 9)
    expected = {
        "macd": _clean(macd_arr),
        "signal": _clean(signal_arr),
        "hist": _clean(hist_arr),
    }
    assert ind.macd(prices) == expected


# ---------------------------------------------------------------------------
# BBANDS
# ---------------------------------------------------------------------------


def test_bbands_matches_talib():
    upper, middle, lower = talib.BBANDS(prices_arr, timeperiod=20, nbdevup=2, nbdevdn=2)
    expected = {
        "upper": _clean(upper),
        "middle": _clean(middle),
        "lower": _clean(lower),
    }
    assert ind.bbands(prices) == expected


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


def test_validation_errors():
    with pytest.raises(ValueError):
        ind.rsi([], 14)
    with pytest.raises(ValueError):
        ind.ema(prices, 0)