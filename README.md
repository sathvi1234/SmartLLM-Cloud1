!# SmartLLM Cloud

SmartLLM Cloud is an LLM optimization middleware that intelligently analyzes prompts, optimizes safe redundancies, routes requests to suitable AI models, and measures real token usage, latency, and estimated cost.

## Inspiration

Modern applications increasingly depend on Large Language Models, but using a single model for every request can lead to unnecessary cost, latency, and resource usage.

Different tasks require different models. A simple question does not always need the most expensive model, while complex reasoning may require a more capable model.

We built SmartLLM Cloud to solve this problem by acting as an intelligent middleware layer between applications and multiple LLM providers.

Instead of sending every request directly to one provider, SmartLLM Cloud analyzes the request, optionally performs conservative prompt optimization, selects a suitable provider/model based on the requested optimization mode, and measures the actual result.

The goal is not to claim theoretical savings, but to provide measurable optimization using real requests.

## What It Does

SmartLLM Cloud provides a unified interface for working with multiple LLM providers.

A user submits a prompt through the Playground.

The system can then:

 1. Analyze the request.
 2. Detect the task complexity.
 3. Safely optimize redundant prompt content when enabled.
 4. Select a suitable provider and model.
 5. Send the request to the real AI provider.
 6. Measure token usage.
 7. Measure latency.
 8. Calculate estimated cost when pricing is available.
 9. Store request metrics.
10. Display analytics and benchmark results.

Supported providers include:

- OpenAI
- Gemini
- Groq
- Ollama

## Core Optimization Modes

### Cost

Prefers the lowest-cost suitable model.

### Speed

Prefers models/providers configured for lower latency.

### Balanced

Uses a combination of capability, estimated cost, and latency.

### Quality

Prefers the highest-capability suitable model.

The routing decision is deterministic and provides an explanation for why a model was selected.

## Prompt Optimization

SmartLLM Cloud includes a conservative prompt optimization layer.

It identifies safe redundancies such as:

- Repeated wording
- Excessive whitespace
- Duplicate instructions
- Unnecessary repetition
- Redundant polite phrases

The optimizer is designed to preserve the original meaning.

It does not modify:

- Code
- SQL
- JSON
- URLs
- Structured data
- Prompts explicitly marked immutable

The system distinguishes between estimated prompt-token reduction and actual provider token usage.

## Model Routing

SmartLLM Cloud maintains centralized model configuration containing information such as:

- Provider
- Model
- Input pricing
- Output pricing
- Capability score
- Context limit
- Availability

The router considers:

- Task complexity
- Provider availability
- Model capability
- Estimated cost
- Latency preference
- Requested output size
- Optimization mode

The UI explains the routing decision instead of silently selecting a model.

## Cost Tracking

When provider/model pricing is available, SmartLLM Cloud calculates:

Input Cost = Input Tokens × Input Price

Output Cost = Output Tokens × Output Price

Total Cost = Input Cost + Output Cost

If pricing information is unavailable, the application displays:

"Pricing unavailable"

rather than inventing a value.

## Real-Time Measurement

Every completed request can record:

- Request ID
- Timestamp
- Provider
- Model
- Input tokens
- Output tokens
- Total tokens
- Latency
- Input cost
- Output cost
- Total cost
- Optimization status
- Optimization reduction
- Routing mode

This allows the application to demonstrate measurable LLM optimization using real requests.

## Playground

The Playground is the primary testing interface.

Users can:

- Enter a prompt
- Select Cost, Speed, Balanced, or Quality mode
- Select Auto or a specific provider/model
- Enable or disable prompt optimization
- Submit the request
- Receive the real provider response

The Playground displays:

### Response

The actual AI-generated response.

### Routing

- Selected provider
- Selected model
- Optimization mode
- Routing reason

### Usage

- Input tokens
- Output tokens
- Total tokens

### Performance

- Latency
- Time to first token when streaming is supported

### Cost

- Input cost
- Output cost
- Total estimated cost

### Optimization

- Original prompt
- Optimized prompt
- Estimated tokens before optimization
- Estimated tokens after optimization
- Reduction percentage

## Benchmark

SmartLLM Cloud includes a benchmark interface for comparing direct LLM execution with SmartLLM execution.

### Direct LLM

Prompt → Baseline Provider/Model → Response

### SmartLLM

Prompt → Analyzer → Optimizer → Router → Selected Model → Response

Both executions measure real:

- Provider
- Model
- Input tokens
- Output tokens
- Total tokens
- Latency
- Estimated cost

The benchmark calculates:

- Token change percentage
- Cost change percentage
- Latency change percentage

No benchmark percentages are hardcoded.

Results are generated from actual executions.

## Analytics

The Analytics dashboard uses stored request data.

It can display:

- Total requests
- Total tokens
- Total estimated cost
- Average latency
- Average tokens per request
- Provider usage
- Model usage
- Cost over time
- Token usage over time
- Latency over time
- Optimization statistics

Supported filters include:

- Today
- Last 7 days
- Last 30 days
- All time

If there is no stored data, the application displays an empty state instead of fake statistics.

## Request History

SmartLLM Cloud maintains request history containing information such as:

- Date
- Provider
- Model
- Tokens
- Latency
- Cost
- Optimization

Individual requests can be opened to view their details.

## Provider Status

The application can report the configuration/availability status of:

- OpenAI
- Gemini
- Groq
- Ollama

The frontend never receives provider API keys.

## Architecture

SmartLLM Cloud uses an existing Next.js frontend and FastAPI backend with an AI provider abstraction.

The core processing flow is:

User Request → Request Analyzer → Prompt Optimizer → Model Router → AI Provider → Response → Token Tracking → Cost Tracking → Latency Tracking → Analytics / Benchmark

## Technology Stack

Frontend:

- Next.js
- React
- TypeScript
- Tailwind CSS
- Existing UI component system

Backend:

- Python
- FastAPI
- Uvicorn
- Pydantic

AI Providers:

- OpenAI
- Gemini
- Groq
- Ollama

Infrastructure:

- Docker
- PostgreSQL configuration
- Redis configuration
- Vercel
- Render

## Deployment

Frontend:

Vercel

Backend:

Render

Production backend:

https://smartllm-cloud1-1.onrender.com

Health endpoint:

https://smartllm-cloud1-1.onrender.com/health

The frontend communicates with the backend through:

NEXT_PUBLIC_API_URL

API keys remain backend-only.

## Security

SmartLLM Cloud does not expose provider API keys to the browser.

Sensitive environment variables remain on the backend.

Examples include:

- OPENAI_API_KEY
- GEMINI_API_KEY
- GROQ_API_KEY

Environment files containing secrets must not be committed to Git.

## Getting Started

Clone the repository:

git clone https://github.com/sathvi1234/SmartLLM-Cloud1.git

Enter the project:

cd SmartLLM-Cloud1

### Backend

Create and configure the backend environment variables.

Start the FastAPI backend using the existing project configuration.

The backend runs locally on:

http://localhost:8000

Health check:

http://localhost:8000/health

### Frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend runs on:

http://localhost:3000

## Production Frontend Configuration

Set the Vercel environment variable:

NEXT_PUBLIC_API_URL=https://smartllm-cloud1-1.onrender.com

After changing the environment variable, redeploy the Vercel frontend.

## Use Cases

SmartLLM Cloud can be used for:

- AI application cost optimization
- Multi-provider LLM routing
- Model selection
- LLM benchmarking
- Token usage monitoring
- AI application analytics
- Prompt optimization
- Latency monitoring
- Provider comparison

## Challenges

Some of the major engineering challenges included:

- Integrating multiple LLM providers through one abstraction
- Building deterministic model routing
- Tracking real token usage
- Handling provider-specific response formats
- Measuring latency accurately
- Implementing safe prompt optimization
- Handling provider availability
- Supporting streaming responses
- Connecting the Vercel frontend with the Render backend
- Handling database availability and fallback behavior
- Preventing API keys from reaching the browser

## What We Learned

Through SmartLLM Cloud we learned how to build middleware around multiple LLM providers while keeping provider implementations independent.

We also learned that LLM optimization should be based on measurable results rather than assumed percentages.

The system therefore focuses on real:

- Token usage
- Cost
- Latency
- Provider selection
- Model selection

## Future Improvements

Future versions can include:

- More LLM providers
- More sophisticated task classification
- Learned routing policies
- Historical latency-based routing
- Advanced prompt optimization
- Automatic model benchmarking
- More detailed cost forecasting
- Team-based analytics
- API usage dashboards
- Enterprise authentication
- Advanced caching
- Arm/Neoverse-aware workload optimization

## Impact

SmartLLM Cloud aims to make multi-model AI applications more efficient by choosing the right model for the right task.

Instead of assuming that one model is best for every request, SmartLLM Cloud measures the request and makes a data-driven routing decision.

The result is an observable optimization layer for modern LLM applications.

## License

Add the project's actual license here if one has been selected



## 📑 Table of Contents
- [About](#-about)
- [How It Works](#-how-it-works)
- [Real-World Use Cases](#-real-world-use-cases)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [File Tree](#-file-tree)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Authentication](#-authentication)
- [Rate Limiting](#-rate-limiting)
- [API Reference](#-api-reference)
- [Error Handling](#-error-handling)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [License](#-license)

---



## 🧾 About
> **Tagline** — One sentence describing the API.

Describe what this API does, what data or service it exposes, and who should integrate with it.

Example:
> The Items API is a RESTful service that manages product catalog data for e-commerce platforms. It provides fast, cached endpoints for reading inventory and authenticated endpoints for catalog management, designed to handle thousands of requests per second.

---



## ⚙️ How It Works
Describe the request lifecycle at a high level:

```
Client Request
    │
    ▼
Rate Limiter → Auth Middleware → Validator → Controller → Service → DB/Cache
    │
    ▼
JSON Response (success or structured error)
```

1. **Auth:** Every request is validated against a JWT or API key.
2. **Validation:** Request body and params are checked with Zod schemas before any business logic runs.
3. **Caching:** Read-heavy endpoints are cached in Redis with TTL-based invalidation.
4. **Response:** All responses follow a consistent envelope format.

---



## 💼 Real-World Use Cases
- **Mobile Apps:** A React Native app calls this API to fetch and update user data without embedding business logic client-side.
- **Third-Party Integrations:** Partners use the public API with scoped API keys to read product data into their own systems.
- **Microservice Communication:** Other internal services call this API as a single source of truth for the resource domain.
- **Webhooks & Automation:** Zapier or Make.com users connect to this API to trigger workflows on data changes.

---



## ✨ Features
- Fully typed with TypeScript
- JWT authentication with refresh token rotation
- Role-based authorization middleware
- Rate limiting per API key / IP
- Request validation with Zod
- Swagger / OpenAPI 3.0 docs
- Structured JSON logging with Pino
- Consistent error response format

---



## 🛠️ Tech Stack
| Layer      | Technology       |
| ---------- | ---------------- |
| Runtime    | Node.js + Bun    |
| Framework  | Fastify          |
| Language   | TypeScript       |
| Validation | Zod              |
| ORM        | Prisma           |
| Database   | PostgreSQL       |
| Caching    | Redis            |
| Docs       | Swagger UI       |
| Testing    | Vitest           |

---



## 📂 File Tree
```
api/
├── src/
│   ├── controllers/      # Route handlers
│   ├── models/           # DB schemas / entities
│   ├── routes/           # API route definitions
│   ├── middleware/        # Auth, rate-limit, error handlers
│   ├── services/         # Business logic layer
│   ├── validators/       # Zod request schemas
│   └── utils/            # Shared helpers
├── prisma/
├── tests/
├── swagger.yml
├── .env.example
└── server.ts
```

---



## 🏁 Getting Started
```bash
git clone https://github.com/username/api-project.git
cd api-project
npm install
cp .env.example .env
npm run db:migrate
npm run dev
```

---



## 💡 Usage



### Make your first request
```bash
# Get all items (public endpoint)
curl https://api.example.com/v1/items

# Create an item (authenticated)
curl -X POST https://api.example.com/v1/items   -H "Authorization: Bearer YOUR_TOKEN"   -H "Content-Type: application/json"   -d '{"name": "My Item", "description": "A great item"}'
```



### SDK / Client Example
```typescript
import { ApiClient } from '@yourorg/api-sdk';

const client = new ApiClient({ apiKey: process.env.API_KEY });

const items = await client.items.list({ page: 1, limit: 20 });
const item  = await client.items.create({ name: 'New Item' });
```

> 📖 Full interactive docs: [https://api.example.com/docs](https://api.example.com/docs)

---



## 🔑 Authentication
```http
Authorization: Bearer <YOUR_TOKEN>
```

**Get a token:**

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "email": "user@example.com", "password": "your_password" }
```

**Response:**
```json
{ "accessToken": "eyJ...", "refreshToken": "eyJ...", "expiresIn": 3600 }
```

---



## 🚦 Rate Limiting
| Tier       | Limit            |
| ---------- | ---------------- |
| Free       | 100 req / hour   |
| Pro        | 1,000 req / hour |
| Enterprise | Unlimited        |

Response headers on every request:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1714000000
```

---



## 📚 API Reference



### Items
| Method   | Endpoint             | Description         | Auth |
| -------- | -------------------- | ------------------- | ---- |
| `GET`    | `/api/v1/items`      | List all items      | No   |
| `GET`    | `/api/v1/items/:id`  | Get a single item   | No   |
| `POST`   | `/api/v1/items`      | Create an item      | Yes  |
| `PUT`    | `/api/v1/items/:id`  | Update an item      | Yes  |
| `DELETE` | `/api/v1/items/:id`  | Delete an item      | Yes  |

---



## ⚠️ Error Handling
All errors follow a consistent format:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested item does not exist.",
    "status": 404
  }
}
```

| Code                  | HTTP | Description                 |
| --------------------- | ---- | --------------------------- |
| `UNAUTHORIZED`        | 401  | Missing or invalid token    |
| `FORBIDDEN`           | 403  | Insufficient permissions    |
| `RESOURCE_NOT_FOUND`  | 404  | Resource does not exist     |
| `VALIDATION_ERROR`    | 422  | Invalid request body/params |
| `RATE_LIMIT_EXCEEDED` | 429  | Too many requests           |
| `INTERNAL_ERROR`      | 500  | Unexpected server error     |

---



## 🧪 Testing
```bash
npm run test                # Unit tests
npm run test:integration    # Integration tests
npm run test:coverage       # Coverage report
```

---



## 🚢 Deployment
```bash
npm run build
npm run start

# Docker
docker build -t api-service .
docker run -p 3000:3000 --env-file .env api-service
```

---



## 📝 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
