FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential wget ca-certificates && \
    # Build TA-Lib from source (binary package may be unavailable on some distros)
    wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make -j"$(nproc)" && \
    make install && \
    cd /app && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz && \
    ldconfig && \
    apt-get purge -y --auto-remove wget && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
ENV TA_INCLUDE_PATH=/usr/include TA_LIBRARY_PATH=/usr/lib
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "app.main"]