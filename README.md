# TA-Lib MCP Server

A production-ready [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server exposing a handful of **technical analysis indicators** powered by [TA-Lib](https://ta-lib.org/).

* ⚡ Built with [FastMCP](https://gofastmcp.com/) – automatic schema generation & HTTP transport out of the box.
* 🔒 Secured by a minimal **Bearer token** middleware – set `MCP_API_KEY` and you are done.
* 🐳 First-class Docker support – `docker-compose up --build` starts it on `http://localhost:8000`.
* ✅ Comprehensive test-suite & CI – indicator math validated against raw TA-Lib values.

---

## Table of contents

1. [Quick start](#quick-start)
2. [Project layout](#project-layout)
3. [Tools / indicators](#tools--indicators)
4. [Authentication](#authentication)
5. [Local development](#local-development)
6. [Running the test-suite](#running-the-test-suite)
7. [CI pipeline](#ci-pipeline)
8. [Docker](#docker)
9. [License](#license)

---

## Quick start

```bash
# 1. Clone & enter repo
$ git clone <repo> && cd talib-mcp-server

# 2. Install system deps (TA-Lib C library)
# Build TA-Lib C library (binary package often unavailable)
$ sudo apt-get install -y build-essential wget
$ wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
$ tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib
$ ./configure --prefix=/usr && make -j"$(nproc)" && sudo make install
$ cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# 3. Create virtualenv & install Python deps
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 4. Configure auth
$ cp .env.example .env            # edit MCP_API_KEY as desired

# 5. Run the server (HTTP on :8000)
$ python -m app.main
```

Visit `http://localhost:8000/tools` with header `Authorization: Bearer <token>` to see the generated MCP tool schema.

## Project layout

```text
talib-mcp-server/
├── app/                # Application code
│   ├── __init__.py
│   ├── auth.py         # Bearer-token middleware
│   ├── indicators.py   # Stateless TA-Lib wrappers
│   └── main.py         # FastMCP server definition
├── tests/              # Pytest unit & integration tests
├── Dockerfile          # Container image (python:3.11-slim)
├── docker-compose.yml  # Convenience runner
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── .github/workflows/ci.yml  # GitHub Actions pipeline
```

## Tools / indicators

| Tool | Signature | Description |
|------|-----------|-------------|
| `rsi` | `rsi(prices: List[float], period: int = 14)` | Relative Strength Index |
| `macd` | `macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9)` | MACD line, signal & histogram |
| `ema` | `ema(prices: List[float], period: int)` | Exponential Moving Average |
| `sma` | `sma(prices: List[float], period: int)` | Simple Moving Average |
| `bbands` | `bbands(prices: List[float], period: int = 20, std_dev: float = 2.0)` | Bollinger Bands upper/middle/lower |

All outputs are JSON-serialisable (floats or `null` when the value cannot yet be computed).

## Authentication

Every MCP endpoint requires:

```
Authorization: Bearer <token>
```

The token must match the value of `MCP_API_KEY` (via environment variable or `.env` file). Unauthorized requests receive `401 {"error": "Unauthorized"}`.

## Example API Calls

Here are some example HTTP requests to demonstrate how to use the MCP server:

### RSI (Relative Strength Index)

```bash
curl -X POST http://localhost:8000/call \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rsi",
    "arguments": {
      "prices": [44.0, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.15, 45.42, 45.84, 46.08, 45.89, 46.03, 46.28, 46.28],
      "period": 14
    }
  }'
```

### MACD (Moving Average Convergence Divergence)

```bash
curl -X POST http://localhost:8000/call \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "macd",
    "arguments": {
      "prices": [12.0, 12.5, 13.0, 12.8, 13.2, 13.1, 13.5, 13.3, 13.8, 14.0, 14.2, 13.9, 14.1, 14.5, 14.3],
      "fast": 12,
      "slow": 26,
      "signal": 9
    }
  }'
```

Response:
```json
{
  "macd": [null, null, ..., 0.123],
  "signal": [null, null, ..., 0.089], 
  "histogram": [null, null, ..., 0.034]
}
```

### Simple Moving Average (SMA)

```bash
curl -X POST http://localhost:8000/call \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sma",
    "arguments": {
      "prices": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
      "period": 5
    }
  }'
```

### Exponential Moving Average (EMA)

```bash
curl -X POST http://localhost:8000/call \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ema",
    "arguments": {
      "prices": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
      "period": 10
    }
  }'
```

### Bollinger Bands

```bash
curl -X POST http://localhost:8000/call \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bbands",
    "arguments": {
      "prices": [20, 21, 19, 22, 20, 23, 21, 24, 22, 25, 23, 26, 24, 27, 25, 28, 26, 29, 27, 30],
      "period": 20,
      "std_dev": 2.0
    }
  }'
```

Response:
```json
{
  "upper": [null, null, ..., 25.8],
  "middle": [null, null, ..., 23.5],
  "lower": [null, null, ..., 21.2]
}
```

### Getting Available Tools

```bash
curl -X GET http://localhost:8000/tools \
  -H "Authorization: Bearer your-api-key"
```

## Local development

```bash
# install pre-commit hooks (flake8, black)
$ pip install pre-commit
$ pre-commit install
```

### Live reload

FastMCP itself doesn’t ship autoreload; use **hot reloaders** like `watchfiles` or run inside your IDE.

## Running the test-suite

```bash
$ MCP_API_KEY=testtoken pytest -q
```

Unit tests compare indicator outputs with TA-Lib to guarantee correctness and exercise auth/error handling for MCP endpoints using Starlette’s `TestClient`.

## CI pipeline

`.github/workflows/ci.yml` runs on every push / PR:

1. Install TA-Lib system libs
2. Install Python deps
3. `flake8` & `black --check`
4. `pytest`
5. Build the Docker image to ensure Dockerfile stays valid

## Docker

```bash
# Build image
$ docker build -t talib-mcp-server .

# Run container with key env var
$ docker run -e MCP_API_KEY=mytoken -p 8000:8000 talib-mcp-server
```

Alternatively:

```bash
$ cp .env.example .env  # customise key
$ docker-compose up --build
```

The server will be available at `http://localhost:8000`.

## License

MIT – © 2025 Your Name