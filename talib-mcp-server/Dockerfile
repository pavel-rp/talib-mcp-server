FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
# TA-Lib’s Python package requires the C library.  Debian provides a packaged
# version (`libta-lib0`).  We also need a compiler for `pip` to build wheels
# when necessary.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libta-lib0 \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------------------
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Application source
# ---------------------------------------------------------------------------
COPY . .

EXPOSE 8000

# Default command runs the FastMCP server via `python -m app.main`, which is
# compatible with both `docker run` and `docker-compose` as specified.
CMD ["python", "-m", "app.main"]