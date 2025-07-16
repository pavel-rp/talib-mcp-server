from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from fastmcp import FastMCP

from app.auth import BearerAuthMiddleware
from app import indicators

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

mcp = FastMCP(
    name="talib-mcp-server",
    instructions="Stateless TA-Lib indicators. Provide prices oldest→newest.",
)

# Attach auth middleware
try:
    mcp.add_middleware(BearerAuthMiddleware)  # FastMCP >=2.5
except AttributeError:
    getattr(mcp, "app").add_middleware(BearerAuthMiddleware)  # type: ignore[attr-defined]


@mcp.tool()
def rsi(prices: List[float], period: int = 14) -> List[float | None]:
    return indicators.rsi(prices, period)


@mcp.tool()
def macd(
    prices: List[float],
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> Dict[str, List[float | None]]:
    return indicators.macd(prices, fastperiod, slowperiod, signalperiod)


@mcp.tool()
def ema(prices: List[float], period: int = 10) -> List[float | None]:
    return indicators.ema(prices, period)


@mcp.tool()
def sma(prices: List[float], period: int = 10) -> List[float | None]:
    return indicators.sma(prices, period)


@mcp.tool()
def bbands(
    prices: List[float],
    period: int = 20,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
) -> Dict[str, List[float | None]]:
    return indicators.bbands(prices, period, nbdevup, nbdevdn)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)