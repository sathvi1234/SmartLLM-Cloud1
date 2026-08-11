from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging

from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Setup OpenTelemetry Tracing Provider
trace.set_tracer_provider(TracerProvider())
# For production, replace ConsoleSpanExporter with OTLPExporter to send traces to Jaeger/Tempo
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Production-ready FastAPI backend for SmartLLM Cloud",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)


@app.on_event("startup")
def _init_database():
    from app.db.session import init_db
    init_db()


app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize Prometheus Metrics Endpoint (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Initialize OpenTelemetry APM Tracing
FastAPIInstrumentor.instrument_app(app)


@app.get("/")
def root():
    return {"message": "Welcome to SmartLLM Cloud API"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "smartllm-api"}
