# Dockerfile for TA-Lib MCP Server
# Building TA-Lib C v0.6.4 from source (GitHub)

# Base Python image - using 3.10 for TA-Lib compatibility
FROM python:3.10-slim

# Install build tools and dependencies for TA-Lib C
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       git \
       autoconf \
       automake \
       libtool \
       pkg-config \
       wget \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone, bootstrap, build & install TA-Lib C v0.6.4
WORKDIR /tmp
RUN git clone --depth 1 --branch v0.6.4 https://github.com/TA-Lib/ta-lib.git \
    && cd ta-lib \
    && sh autogen.sh \
    && ./configure --prefix=/usr \
    && make -j$(nproc) \
    && make install

# Set library path
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH

# Prepare application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and run
EXPOSE 8000
CMD ["python", "-m", "app.main"]