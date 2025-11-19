# HDHomeRun Channel Scanner - Production Dockerfile
# Version 3.0
# Base image: Python 3.11 slim for smaller footprint

FROM python:3.11-slim

# Metadata
LABEL maintainer="HDHomeRun Scanner Team"
LABEL version="3.0"
LABEL description="HDHomeRun Channel Scanner - Network TV tuner utility"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Create non-root user for security
RUN groupadd -r hdhr && useradd -r -g hdhr -m -s /bin/bash hdhr

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install hdhomerun_config utility
RUN curl -L -o /tmp/libhdhomerun.tgz \
    https://download.silicondust.com/hdhomerun/libhdhomerun_20210624.tgz \
    && tar -xzf /tmp/libhdhomerun.tgz -C /tmp \
    && cd /tmp/libhdhomerun && make \
    && cp hdhomerun_config /usr/local/bin/ \
    && chmod +x /usr/local/bin/hdhomerun_config \
    && rm -rf /tmp/libhdhomerun*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY README.md .
COPY ERROR_REFERENCE.md .

# Create output directories
RUN mkdir -p /app/output /app/logs && \
    chown -R hdhr:hdhr /app

# Switch to non-root user
USER hdhr

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD hdhomerun_config discover || exit 1

# Default command (can be overridden)
CMD ["python3", "main.py", "--help"]
