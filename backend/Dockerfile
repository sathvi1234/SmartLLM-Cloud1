# Build stage
FROM python:3.11-slim as builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final production stage
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies and curl for healthchecks
RUN apt-get update && apt-get install -y libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . .

# Run as non-root user for security (OWASP)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Render (and other hosts) inject PORT; default 8000 for local/docker-compose.
EXPOSE 8000

# Use the root /health endpoint (no auth, no DB). Expand PORT at container runtime.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD sh -c 'curl -f http://127.0.0.1:${PORT:-8000}/health || exit 1'

# Listen on 0.0.0.0 and Render's PORT (fallback 8000).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
