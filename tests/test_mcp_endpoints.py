import pathlib
import sys

# Ensure project root on sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pytest
from starlette.testclient import TestClient

from app.main import mcp


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "testtoken")
    yield
    monkeypatch.delenv("MCP_API_KEY", raising=False)


@pytest.fixture()
def client():
    app = getattr(mcp, "app", None) or getattr(mcp, "starlette_app", None)
    return TestClient(app)


def test_auth(client):
    assert client.get("/tools").status_code == 401
    r = client.get("/tools", headers={"Authorization": "Bearer testtoken"})
    assert r.status_code == 200
    assert "rsi" in r.json()


def test_call_sma(client):
    payload = {
        "name": "sma",
        "arguments": {"prices": list(range(1, 11)), "period": 5},
    }
    r = client.post(
        "/call",
        json=payload,
        headers={"Authorization": "Bearer testtoken"},
    )
    assert r.status_code == 200
    assert "result" in r.json()