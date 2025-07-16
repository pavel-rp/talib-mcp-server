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
| `macd` | `macd(prices: List[float], fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9)` | MACD line, signal & histogram |
| `ema` | `ema(prices: List[float], period: int = 10)` | Exponential Moving Average |
| `sma` | `sma(prices: List[float], period: int = 10)` | Simple Moving Average |
| `bbands` | `bbands(prices: List[float], period: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0)` | Bollinger Bands upper/middle/lower |

All outputs are JSON-serialisable (floats or `null` when the value cannot yet be computed).

## Authentication

Every MCP endpoint requires:

```
Authorization: Bearer <token>
```

The token must match the value of `MCP_API_KEY` (via environment variable or `.env` file). Unauthorized requests receive `401 {"error": "Unauthorized"}`.

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