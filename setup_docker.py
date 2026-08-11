import os

files = {
    "backend/Dockerfile": """# Build stage
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

EXPOSE 8000

# Healthcheck targeting the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "Dockerfile": """FROM node:20-alpine AS base

# 1. Install dependencies
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# 2. Build the source code
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# 3. Production runner
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Security: non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app ./
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Healthcheck targeting frontend root
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "start"]
""",
    "docker-compose.yml": """version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: smartllm-db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: supersecretpassword
      POSTGRES_DB: smartllm
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - smartllm_network
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d smartllm"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: smartllm-cache
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - smartllm_network
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: smartllm-api
    restart: always
    environment:
      - DATABASE_URL=postgresql://postgres:supersecretpassword@postgres:5432/smartllm
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=production_secret_key_change_me_immediately_in_deployment
      - API_V1_STR=/api/v1
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - smartllm_network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: smartllm-web
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_started
    networks:
      - smartllm_network

networks:
  smartllm_network:
    driver: bridge

volumes:
  postgres_data:
    name: smartllm_postgres_data
  redis_data:
    name: smartllm_redis_data
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Docker configurations generated successfully.")
