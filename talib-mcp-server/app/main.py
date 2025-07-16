from __future__ import annotations

"""Entry-point for the TA-Lib MCP server.

This module wires together:

* **FastMCP** server instance named ``talib-mcp-server``
* Indicator tool registrations (wrapping functions in :pymod:`app.indicators`)
* Bearer-token authentication middleware (:class:`app.auth.BearerAuthMiddleware`)
* ``dotenv`` support so that ``MCP_API_KEY`` can be configured in a ``.env``
  file for local development.

Run directly (e.g. ``python -m app.main``) or via ``fastmcp run``.  By default
it serves over *streamable HTTP* on port **8000** as required by the project
specification.
"""

from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from fastmcp import FastMCP

from app.auth import BearerAuthMiddleware
from app import indicators

# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

# Automatically load variables from a `.env` at project root if present.
# This is convenient for local development while remaining optional in
# production where environment variables would be injected by the container
# orchestration platform.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env", override=False)

# ---------------------------------------------------------------------------
# Server definition
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="talib-mcp-server",
    instructions=(
        "Stateless TA-Lib technical indicators.  Supply a list of prices in\n"
        "chronological order (oldest ➔ newest).  All numeric outputs that\n"
        "cannot be computed yet are returned as `null` for JSON
        "serialisability."
    ),
    # Streamable HTTP is recommended for web deployments.
    transport="http",
    host="0.0.0.0",
    port=8000,
)

# Attach authentication middleware **before** any other logic.
try:
    mcp.add_middleware  # FastMCP >= 2.5 exposes the Starlette-style helper
except AttributeError:
    # Older FastMCP versions expose the underlying Starlette `app` via
    # `mcp.app`.  Fall back to that.
    _starlette_app = getattr(mcp, "app", None) or getattr(mcp, "starlette_app", None)
    if _starlette_app is None:
        raise RuntimeError("Could not locate the underlying ASGI application to attach middleware")
    _starlette_app.add_middleware(BearerAuthMiddleware)
else:
    mcp.add_middleware(BearerAuthMiddleware)

# ---------------------------------------------------------------------------
# Tool registrations
# ---------------------------------------------------------------------------

# We create *wrapper* functions that delegate to the pure implementations in
# `app.indicators`.  This keeps the core indicator logic decoupled from MCP and
# allows us to add additional validation layers if required.


@mcp.tool()
def rsi(prices: List[float], period: int = 14) -> List[float | None]:
    """Relative Strength Index (RSI).  See :func:`app.indicators.rsi`."""

    return indicators.rsi(prices, period)


@mcp.tool()
def macd(
    prices: List[float],
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> Dict[str, List[float | None]]:
    """Moving Average Convergence/Divergence (MACD).  See :func:`app.indicators.macd`."""

    return indicators.macd(prices, fastperiod, slowperiod, signalperiod)


@mcp.tool()
def ema(prices: List[float], period: int = 10) -> List[float | None]:
    """Exponential Moving Average (EMA).  See :func:`app.indicators.ema`."""

    return indicators.ema(prices, period)


@mcp.tool()
def sma(prices: List[float], period: int = 10) -> List[float | None]:
    """Simple Moving Average (SMA)."""

    return indicators.sma(prices, period)


@mcp.tool()
def bbands(
    prices: List[float],
    period: int = 20,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
) -> Dict[str, List[float | None]]:
    """Bollinger Bands (BBANDS)."""

    return indicators.bbands(prices, period, nbdevup, nbdevdn)


# ---------------------------------------------------------------------------
# Script entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Note: When using `fastmcp run app.main:mcp --transport http`, the CLI will
    #       bypass this block and invoke `mcp.run()` directly with its own
    #       parameters.  Including it here ensures `python -m app.main` still
    #       works out of the box for local testing.
    mcp.run()