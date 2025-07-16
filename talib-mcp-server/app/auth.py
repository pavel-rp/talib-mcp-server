from __future__ import annotations

"""Authentication utilities for the TA-Lib MCP server.

Currently implements a simple **Bearer token** middleware that checks the
``Authorization`` header against the static ``MCP_API_KEY`` environment
variable loaded from ``.env`` (see `python-dotenv`).

If a request is unauthenticated, the middleware returns a *401 Unauthorized*
response in the format required by the project specification::

    HTTP/1.1 401 Unauthorized
    Content-Type: application/json

    {"error": "Unauthorized"}

This middleware should be added **before** any other business logic so that
all MCP endpoints are protected.
"""

from os import getenv
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

__all__ = ["BearerAuthMiddleware", "get_api_key_or_raise"]


def _unauthorized() -> Response:
    """Return a 401 *Unauthorized* JSON response."""

    return JSONResponse({"error": "Unauthorized"}, status_code=401)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that validates *Bearer* tokens.

    The expected token is taken from the ``MCP_API_KEY`` environment
    variable.  For convenience during local development, you can define it in
    a ``.env`` file loaded via :pypi:`python-dotenv`.
    """

    def __init__(self, app, api_key: Optional[str] | str = None) -> None:  # type: ignore[override]
        super().__init__(app)
        self._api_key: str | None = api_key or getenv("MCP_API_KEY")
        if not self._api_key:
            raise RuntimeError("MCP_API_KEY environment variable is not set—authentication cannot be enforced.")

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        # Skip authentication for health-check or root endpoints if desired
        # (adjust the condition to your needs). For now, we protect *all* routes.
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return _unauthorized()

        token = auth_header.split(" ", 1)[1].strip()
        if token != self._api_key:
            return _unauthorized()

        return await call_next(request)


def get_api_key_or_raise() -> str:
    """Utility to access the configured API key elsewhere in the codebase."""

    api_key = getenv("MCP_API_KEY")
    if not api_key:
        raise RuntimeError("MCP_API_KEY environment variable is not set.")
    return api_key