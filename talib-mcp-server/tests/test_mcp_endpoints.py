import os
import asyncio

import pytest
from starlette.testclient import TestClient

from app.main import mcp


@pytest.fixture(autouse=True)
def _set_api_key_env(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "testtoken")
    yield
    monkeypatch.delenv("MCP_API_KEY", raising=False)


@pytest.fixture()
def client():
    # The underlying Starlette application is exposed via `mcp.app` in FastMCP
    starlette_app = getattr(mcp, "app", None) or getattr(mcp, "starlette_app", None)
    return TestClient(starlette_app)


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------

def test_unauthorized_request(client):
    resp = client.get("/tools")
    assert resp.status_code == 401
    assert resp.json() == {"error": "Unauthorized"}


def test_authorized_request_tools(client):
    resp = client.get("/tools", headers={"Authorization": "Bearer testtoken"})
    assert resp.status_code == 200
    assert "rsi" in resp.json()


# ---------------------------------------------------------------------------
# Tool execution via /call
# ---------------------------------------------------------------------------

def test_tool_execution_success(client):
    payload = {
        "name": "sma",
        "arguments": {"prices": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "period": 5},
    }
    resp = client.post("/call", json=payload, headers={"Authorization": "Bearer testtoken"})
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data


# ---------------------------------------------------------------------------
# Parameter validation error should return 400
# ---------------------------------------------------------------------------

def test_parameter_validation_error(client):
    payload = {"name": "rsi", "arguments": {"prices": [], "period": 14}}
    resp = client.post("/call", json=payload, headers={"Authorization": "Bearer testtoken"})
    assert resp.status_code == 400 or resp.status_code == 422