# WolfPy Production Dockerfile
# Multi-stage build for optimized production deployment

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and production dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .[production] && \
    pip install build

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    WOLFPY_ENV=production \
    PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application user
RUN groupadd -r wolfpy && useradd -r -g wolfpy wolfpy

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=wolfpy:wolfpy . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/templates && \
    chown -R wolfpy:wolfpy /app

# Switch to non-root user
USER wolfpy

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
