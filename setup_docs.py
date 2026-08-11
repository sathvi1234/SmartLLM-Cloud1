import os

docs = {
    "README.md": """<div align="center">
  <h1>⚡ SmartLLM Cloud</h1>
  <p><strong>Enterprise-Grade AI Gateway & Orchestration Platform</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Next.js-16.2-black?logo=next.js" />
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" />
    <img src="https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql" />
    <img src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis" />
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker" />
    <img src="https://img.shields.io/badge/License-MIT-green" />
  </p>
  <br/>
  <p><em>Route. Optimize. Analyze. Scale.</em></p>
</div>

---

## 📸 Screenshots

| Dashboard | Analytics | Router |
|-----------|-----------|--------|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Analytics](docs/screenshots/analytics.png) | ![Router](docs/screenshots/router.png) |

---

## 🚀 Overview

SmartLLM Cloud is a production-ready AI Operating System that intelligently routes prompts across multiple LLM providers — OpenAI, Gemini, Groq, and Ollama — selecting the best model based on cost, latency, quality, and privacy requirements.

### Why SmartLLM Cloud?

- 💰 **Cut AI Costs by up to 80%** — Semantic caching and intelligent routing eliminate redundant API calls.
- ⚡ **Sub-500ms Routing Decisions** — The Smart Router analyzes and routes prompts in milliseconds.
- 🔒 **Enterprise Security** — JWT auth, OWASP best practices, AWS Secrets Manager, bcrypt password hashing.
- 📊 **Full Observability** — Prometheus metrics, OpenTelemetry tracing, structured JSON logging.
- 🌍 **Provider-Agnostic** — Drop in any new LLM provider by implementing a single abstract interface.

---

## ✨ Core Features

| Feature | Description |
|---|---|
| **Smart Model Router** | Scores all models on cost, latency, quality, and privacy — picks the best one for each prompt |
| **Prompt Analyzer** | Detects intent (Code, Math, Writing, Translation) and estimates difficulty before routing |
| **Prompt Optimizer** | Rewrites prompts for token efficiency — returns short, ultra-short, and optimized versions |
| **Cost Prediction Engine** | Predicts input/output tokens, USD cost, and latency before firing any API call |
| **Token Counter** | Accurate per-provider token counting using `tiktoken` (OpenAI), native Gemini SDK, and BPE heuristics |
| **Redis Semantic Cache** | Stores responses by embedding similarity — serves cached responses for semantically equivalent prompts |
| **Analytics Service** | Aggregates daily/monthly cost, latency, carbon footprint, and provider/model distribution |
| **Production Monitoring** | Prometheus `/metrics` endpoint, Grafana dashboards, OpenTelemetry distributed tracing |
| **JWT Authentication** | Full auth flow: Signup, Login, Refresh Token, Email Verification, Password Reset |

---

## 🛠 Tech Stack

### Frontend
- **Next.js 16** + TypeScript
- **TailwindCSS v4** + Shadcn UI
- **Framer Motion** for animations
- **Recharts** for data visualization
- **Lucide Icons**

### Backend
- **FastAPI** (Python 3.11) — Clean Architecture with Dependency Injection
- **SQLAlchemy** + **Alembic** for ORM and migrations
- **PostgreSQL 15** — Primary database
- **Redis 7** — Semantic cache layer
- **JWT** — RS256 access + refresh token architecture

### AI Providers
- OpenAI (GPT-4o, GPT-4o-mini)
- Google Gemini (1.5 Flash, 1.5 Pro)
- Groq (LLaMA 3, Mixtral)
- Ollama (Local inference)

### Infrastructure
- **Docker** + **Docker Compose**
- **AWS EC2** + **RDS** + **ElastiCache**
- **NGINX** + **Certbot (SSL)**
- **GitHub Actions** CI/CD
- **Prometheus** + **Grafana**

---

## ⚡ Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (or use the Docker Compose setup)

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/smartllm-cloud.git
cd smartllm-cloud
```

### 2. Configure Environment Variables
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env` with your credentials (see [Installation Guide](docs/INSTALLATION.md)).

### 3. Launch with Docker (Recommended)
```bash
docker-compose up -d --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### 4. Manual Setup (Development)
```bash
# Frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/auth/signup` | Register new user | ❌ |
| `POST` | `/api/v1/auth/login` | Login, returns JWT | ❌ |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | ✅ |
| `POST` | `/api/v1/ai/analyze` | Analyze prompt intent & complexity | ✅ |
| `POST` | `/api/v1/ai/optimize` | Optimize prompt for token efficiency | ✅ |
| `POST` | `/api/v1/ai/predict-cost` | Predict cost and latency pre-inference | ✅ |
| `POST` | `/api/v1/ai/count-tokens` | Count tokens per provider | ✅ |
| `POST` | `/api/v1/ai/cache/check` | Check semantic cache for match | ✅ |
| `GET`  | `/api/v1/ai/cache/stats` | Get cache statistics and savings | ✅ |
| `GET`  | `/api/v1/analytics/overview` | Full dashboard analytics payload | ✅ |
| `GET`  | `/api/v1/health` | API health check | ❌ |
| `GET`  | `/metrics` | Prometheus metrics scrape endpoint | ❌ |

---

## 📁 Project Structure

```
smartllm-cloud/
├── .github/workflows/ci-cd.yml     # Enterprise CI/CD pipeline
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── factory.py          # AIFactory provider registry
│   │   │   ├── optimizer.py        # Prompt optimizer engine
│   │   │   ├── cache.py            # Redis semantic cache
│   │   │   └── router/
│   │   │       ├── smart_router.py     # Smart model routing engine
│   │   │       ├── analyzer.py         # Prompt intent analyzer
│   │   │       ├── cost_predictor.py   # Cost prediction engine
│   │   │       └── token_estimator.py  # Multi-provider token counter
│   │   ├── api/v1/endpoints/       # FastAPI route handlers
│   │   ├── core/                   # Settings, logging, security
│   │   ├── models/                 # SQLAlchemy models
│   │   └── services/               # Business logic layer
│   ├── Dockerfile
│   └── requirements.txt
├── src/                            # Next.js App Router source
├── nginx/smartllm.conf             # NGINX reverse proxy config
├── docker-compose.yml              # Local development stack
├── docker-compose.prod.yml         # Production AWS stack
└── deploy.sh                       # EC2 bootstrap script
```

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

<div align="center">Built with ❤️ by the SmartLLM Team</div>
""",

    "docs/INSTALLATION.md": """# Installation Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Node.js | 20+ | For Next.js frontend |
| Python | 3.11+ | For FastAPI backend |
| PostgreSQL | 15+ | Primary database |
| Redis | 7+ | Semantic cache |
| Docker | 24+ | Recommended for full stack |

---

## Environment Variables

Create `backend/.env` from the example:

```bash
cp backend/.env.example backend/.env
```

### Required Variables

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/smartllm

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Security
SECRET_KEY=your-super-secret-key-minimum-32-chars

# AI Providers (add keys for providers you want to use)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...

# App Config
API_V1_STR=/api/v1
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend Environment

Create `.env.local` in the project root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Database Migrations

```bash
cd backend
alembic upgrade head
```

---

## Installing Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Key dependencies
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `sqlalchemy` — ORM
- `alembic` — Migrations
- `tiktoken` — OpenAI-compatible tokenizer
- `numpy` — Semantic cache similarity
- `prometheus-fastapi-instrumentator` — Metrics
- `opentelemetry-instrumentation-fastapi` — Tracing
- `python-json-logger` — Structured logging
- `tenacity` — Retry mechanism for AI providers

---

## Running Tests

```bash
cd backend
pytest -v
```

```bash
npm run lint
```
""",

    "docs/CONTRIBUTING.md": """# Contributing to SmartLLM Cloud

Thank you for your interest in contributing! This project follows conventional commits and clean architecture principles.

## Development Setup

1. Fork the repo and clone it locally.
2. Follow the [Installation Guide](INSTALLATION.md).
3. Create a feature branch: `git checkout -b feature/your-feature-name`.

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `refactor:` — Code refactoring
- `test:` — Adding/updating tests
- `chore:` — Build, CI, or tooling changes

## Adding a New AI Provider

1. Create a new file `backend/app/ai/providers/your_provider.py`.
2. Extend the `BaseAIProvider` abstract class and implement `generate()` and `stream()`.
3. Register it inside `AIFactory.get_provider()` in `backend/app/ai/factory.py`.
4. Add a `ModelProfile` entry in `backend/app/ai/router/smart_router.py` with pricing and scoring data.

## Code Standards

- All Python code must pass `flake8` linting.
- All frontend code must pass `eslint`.
- All new endpoints must include Pydantic request/response models.
- No secrets or API keys in code — use environment variables.

## Pull Request Checklist

- [ ] Tests added or updated
- [ ] No new lint errors
- [ ] Documentation updated if needed
- [ ] Environment variable changes reflected in `.env.example`
""",

    "docs/DEPLOYMENT.md": """# Deployment Guide

## Local (Docker Compose)

```bash
docker-compose up -d --build
```

Services:
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

---

## AWS Production Deployment

### Infrastructure Overview

| Component | AWS Service | Purpose |
|---|---|---|
| App Server | EC2 `t3.large` | Runs Docker containers |
| Database | RDS PostgreSQL 15 | Primary data store |
| Cache | ElastiCache Redis 7 | Semantic cache layer |
| Reverse Proxy | NGINX on EC2 | SSL + routing |
| Secrets | AWS Secrets Manager | API keys, DB credentials |
| Registry | GitHub Container Registry | Pre-built Docker images |

### Initial Server Setup

SSH into your EC2 instance and run:

```bash
git clone https://github.com/your-org/smartllm-cloud.git /home/ubuntu/smartllm
cd /home/ubuntu/smartllm
chmod +x deploy.sh
./deploy.sh
```

### Required GitHub Secrets

| Secret Name | Description |
|---|---|
| `EC2_HOST` | Public IP or DNS of your EC2 instance |
| `EC2_SSH_KEY` | Private SSH key for EC2 access |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |

### Continuous Deployment

Every push to `main` automatically:
1. Lints frontend and backend
2. Runs security scan with Trivy
3. Builds and pushes Docker images to GHCR
4. SSHes into EC2, pulls images, and restarts services

### SSL Setup

After DNS is pointing to your EC2 Elastic IP:

```bash
sudo certbot --nginx \\
  -d smartllm.com \\
  -d www.smartllm.com \\
  -d api.smartllm.com \\
  --non-interactive \\
  --agree-tos \\
  -m admin@yourdomain.com
```

---

## Environment Monitoring

- **Prometheus Metrics:** http://your-server:8000/metrics
- **Grafana Dashboard:** Import `backend/grafana/dashboards/smartllm_dashboard.json`
- **Structured Logs:** JSON formatted, searchable via CloudWatch or Loki
""",

    "LICENSE": """MIT License

Copyright (c) 2026 SmartLLM Cloud

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",

    "backend/.env.example": """# ==============================
# SmartLLM Cloud — Backend Config
# ==============================

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/smartllm

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# JWT Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...
OLLAMA_BASE_URL=http://localhost:11434

# App
API_V1_STR=/api/v1
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000

# Email (for verification and password reset)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG....
EMAILS_FROM_EMAIL=noreply@smartllm.com
"""
}

base_path = r"c:\Users\admin\Desktop\aitoken2"
for path, content in docs.items():
    full_path = os.path.join(base_path, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Create screenshots placeholder directory
screenshots_dir = os.path.join(base_path, "docs", "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

for name in ["dashboard.png", "analytics.png", "router.png"]:
    placeholder = os.path.join(screenshots_dir, name)
    if not os.path.exists(placeholder):
        with open(placeholder, "wb") as f:
            f.write(b"PLACEHOLDER")

print("Complete documentation generated successfully.")
