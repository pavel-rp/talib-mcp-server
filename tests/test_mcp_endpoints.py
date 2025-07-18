import pathlib
import sys

# Ensure project root on sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pytest

from app.main import mcp
from app import indicators


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "testtoken")
    yield
    monkeypatch.delenv("MCP_API_KEY", raising=False)


def test_mcp_server_creation():
    # Test that the MCP server was created successfully
    assert mcp is not None
    assert mcp.name == "talib-mcp-server"


@pytest.mark.asyncio
async def test_tools_are_registered():
    # Test that all expected tools are registered
    tools = await mcp.get_tools()
    tool_names = [tool if isinstance(tool, str) else tool.name for tool in tools]

    expected_tools = {"rsi", "macd", "ema", "sma", "bbands"}
    assert expected_tools.issubset(set(tool_names))


def test_tool_execution():
    # Test that tools can be executed by calling the indicators directly
    prices = [44.0, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.15, 45.42, 45.84]

    # Test RSI
    result = indicators.rsi(prices, period=5)
    assert isinstance(result, list)
    assert len(result) == len(prices)

    # Test SMA
    result = indicators.sma(prices, period=5)
    assert isinstance(result, list)
    assert len(result) == len(prices)

    # Test EMA
    result = indicators.ema(prices, period=5)
    assert isinstance(result, list)
    assert len(result) == len(prices)

    # Test MACD - using correct dictionary keys
    result = indicators.macd(prices, fast=3, slow=5, signal=2)
    assert isinstance(result, dict)
    assert set(result.keys()) == {"macd", "signal", "histogram"}

    # Test Bollinger Bands - using correct dictionary keys and parameter names
    result = indicators.bbands(prices, period=5, std_dev=2.0)
    assert isinstance(result, dict)
    assert set(result.keys()) == {"upper", "middle", "lower"}