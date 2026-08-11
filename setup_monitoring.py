import os

files = {
    "backend/app/core/logging.py": """import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove default handlers to prevent duplicate logging
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
        
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s %(span_id)s',
        rename_fields={"levelname": "level", "asctime": "timestamp"}
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Add a global filter to inject trace_id if available via OpenTelemetry
    class TraceFilter(logging.Filter):
        def filter(self, record):
            from opentelemetry import trace
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                record.trace_id = format(span.get_span_context().trace_id, "032x")
                record.span_id = format(span.get_span_context().span_id, "016x")
            else:
                record.trace_id = None
                record.span_id = None
            return True
            
    logger.addFilter(TraceFilter())
""",
    "backend/grafana/dashboards/smartllm_dashboard.json": """{
  "title": "SmartLLM Operations Dashboard",
  "tags": ["smartllm", "production", "fastapi"],
  "timezone": "browser",
  "refresh": "5s",
  "panels": [
    {
      "type": "timeseries",
      "title": "HTTP Request Rate",
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[1m])) by (method, handler)",
          "legendFormat": "{{method}} {{handler}}"
        }
      ]
    },
    {
      "type": "timeseries",
      "title": "Error Rate (Alerting - 5xx)",
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{status=~\\"5..\\"}[1m]))",
          "legendFormat": "5xx Errors"
        }
      ],
      "alert": {
        "name": "High 5xx Error Rate",
        "conditions": [
          {
            "evaluator": {"params": [5], "type": "gt"},
            "operator": {"type": "and"},
            "query": {"params": ["A", "5m", "now"]},
            "reducer": {"type": "avg"}
          }
        ]
      }
    },
    {
      "type": "heatmap",
      "title": "API Latency Distribution",
      "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
      "targets": [
        {
          "expr": "sum(rate(http_request_duration_seconds_bucket[5m])) by (le)",
          "format": "heatmap"
        }
      ],
      "color": {
        "mode": "opacity"
      }
    }
  ]
}
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Update requirements.txt
req_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/requirements.txt")
with open(req_path, "r", encoding="utf-8") as f:
    req_content = f.read()

new_deps = ["prometheus-fastapi-instrumentator", "opentelemetry-api", "opentelemetry-sdk", "opentelemetry-instrumentation-fastapi", "python-json-logger"]
for dep in new_deps:
    if dep not in req_content:
        with open(req_path, "a", encoding="utf-8") as f:
            f.write(f"{dep}\\n")

# Update main.py
main_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/app/main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

if "PrometheusInstrumentator" not in main_content:
    new_imports = """
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Setup OpenTelemetry Tracing Provider
trace.set_tracer_provider(TracerProvider())
# For production, replace ConsoleSpanExporter with OTLPExporter to send traces to Jaeger/Tempo
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
"""
    # Insert after imports
    main_content = main_content.replace("from app.core.logging import setup_logging", "from app.core.logging import setup_logging\\n" + new_imports)
    
    # Insert instrumentator after router include
    instrumentator_code = """
app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize Prometheus Metrics Endpoint (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Initialize OpenTelemetry APM Tracing
FastAPIInstrumentor.instrument_app(app)
"""
    main_content = main_content.replace("app.include_router(api_router, prefix=settings.API_V1_STR)", instrumentator_code)
    
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)

print("Production monitoring setup completed successfully.")
