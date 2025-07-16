from __future__ import annotations

"""Authentication utilities for the TA-Lib MCP server.

Currently implements a simple **Bearer token** middleware that checks the
``Authorization`` header against the static ``MCP_API_KEY`` environment
variable loaded from ``.env``.

If a request is unauthenticated, the middleware returns a *401 Unauthorized*
response ::

    {"error": "Unauthorized"}
"""

from os import getenv
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

__all__ = ["BearerAuthMiddleware", "get_api_key_or_raise"]


def _unauthorized() -> Response:
    return JSONResponse({"error": "Unauthorized"}, status_code=401)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validate Bearer token against MCP_API_KEY env var."""

    def __init__(self, app, api_key: Optional[str] | str = None) -> None:  # type: ignore[override]
        super().__init__(app)
        self._api_key: str | None = api_key or getenv("MCP_API_KEY")
        if not self._api_key:
            raise RuntimeError("MCP_API_KEY environment variable is not set.")

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return _unauthorized()
        token = auth.split(" ", 1)[1].strip()
        if token != self._api_key:
            return _unauthorized()
        return await call_next(request)


def get_api_key_or_raise() -> str:
    api_key = getenv("MCP_API_KEY")
    if not api_key:
        raise RuntimeError("MCP_API_KEY environment variable is not set.")
    return api_key