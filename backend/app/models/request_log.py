import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.models.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class RequestLog(Base):
    """One row per completed LLM request (playground, benchmark, direct)."""

    __tablename__ = "request_logs"

    id = Column(String(36), primary_key=True, default=_uuid, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    provider = Column(String(32), nullable=False)
    model = Column(String(128), nullable=False)
    routing_mode = Column(String(32), default="direct")  # direct|cost|speed|balanced|quality
    source = Column(String(32), default="playground")    # playground|benchmark_direct|benchmark_smart

    prompt_preview = Column(Text, nullable=True)
    response_preview = Column(Text, nullable=True)

    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)

    input_cost_usd = Column(Float, nullable=True)
    output_cost_usd = Column(Float, nullable=True)
    total_cost_usd = Column(Float, nullable=True)
    pricing_available = Column(Boolean, default=True)

    optimization_enabled = Column(Boolean, default=False)
    optimization_reduction_percent = Column(Float, default=0.0)

    def to_dict(self) -> dict:
        return {
            "request_id": self.id,
            "timestamp": self.created_at.isoformat() + "Z" if self.created_at else None,
            "provider": self.provider,
            "model": self.model,
            "routing_mode": self.routing_mode,
            "source": self.source,
            "prompt_preview": self.prompt_preview,
            "response_preview": self.response_preview,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "input_cost_usd": self.input_cost_usd,
            "output_cost_usd": self.output_cost_usd,
            "total_cost_usd": self.total_cost_usd,
            "pricing_available": self.pricing_available,
            "optimization_enabled": self.optimization_enabled,
            "optimization_reduction_percent": self.optimization_reduction_percent,
        }
