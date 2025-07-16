import math
import pathlib
import sys

# Add project root to PYTHONPATH for CI environments
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import numpy as np
import pytest
import talib

from app import indicators as ind


prices = list(range(1, 31))
arr = np.array(prices, dtype=float)


def _clean(a):
    return [None if math.isnan(x) else pytest.approx(float(x)) for x in a]


def test_rsi():
    assert ind.rsi(prices) == _clean(talib.RSI(arr, timeperiod=14))


def test_ema():
    assert ind.ema(prices, 10) == _clean(talib.EMA(arr, timeperiod=10))


def test_sma():
    assert ind.sma(prices, 10) == _clean(talib.SMA(arr, timeperiod=10))


def test_macd():
    m, s, h = talib.MACD(arr, 12, 26, 9)
    expected = {"macd": _clean(m), "signal": _clean(s), "hist": _clean(h)}
    assert ind.macd(prices) == expected


def test_bbands():
    upper, middle, lower = talib.BBANDS(arr, timeperiod=20)
    expected = {"upper": _clean(upper), "middle": _clean(middle), "lower": _clean(lower)}
    assert ind.bbands(prices) == expected