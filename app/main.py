from __future__ import annotations

from pathlib import Path

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
def rsi(prices: list[float], period: int = 14) -> list[float | None]:
    return indicators.rsi(prices, period)


@mcp.tool()
def macd(
    prices: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict[str, list[float | None]]:
    return indicators.macd(prices, fast, slow, signal)


@mcp.tool()
def ema(prices: list[float], period: int = 10) -> list[float | None]:
    return indicators.ema(prices, period)


@mcp.tool()
def sma(prices: list[float], period: int = 10) -> list[float | None]:
    return indicators.sma(prices, period)


@mcp.tool()
def bbands(
    prices: list[float],
    period: int = 20,
    upper_dev: float = 2.0,
    lower_dev: float = 2.0,
) -> dict[str, list[float | None]]:
    return indicators.bbands(prices, period, upper_dev, lower_dev)


# Expose app for testing
app = mcp.http_app()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)