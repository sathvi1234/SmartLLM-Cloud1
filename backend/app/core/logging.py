import logging
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
