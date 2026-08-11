"""Analytics computed from real stored requests. No fabricated numbers:
when there is no data we say so explicitly via has_data=False."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

_RANGES = {
    "today": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
    "all": None,
}


class AnalyticsService:
    def get_overview(self, time_range: str = "all") -> Dict[str, Any]:
        delta = _RANGES.get(time_range, None)
        since: Optional[datetime] = datetime.utcnow() - delta if delta else None

        try:
            db = SessionLocal()
        except Exception:
            return {"has_data": False, "database_available": False, "range": time_range}

        try:
            q = db.query(RequestLog)
            if since is not None:
                q = q.filter(RequestLog.created_at >= since)

            total_requests = q.count()
            if total_requests == 0:
                return {"has_data": False, "database_available": True, "range": time_range}

            def _filtered(query):
                return query.filter(RequestLog.created_at >= since) if since is not None else query

            sums = _filtered(
                db.query(
                    func.coalesce(func.sum(RequestLog.total_tokens), 0),
                    func.coalesce(func.sum(RequestLog.input_tokens), 0),
                    func.coalesce(func.sum(RequestLog.output_tokens), 0),
                    func.coalesce(func.sum(RequestLog.total_cost_usd), 0.0),
                    func.coalesce(func.avg(RequestLog.latency_ms), 0.0),
                )
            ).one()
            total_tokens, input_tokens, output_tokens, total_cost, avg_latency = sums

            provider_usage = [
                {"provider": p, "requests": c, "tokens": int(t or 0), "cost_usd": round(cost or 0.0, 6)}
                for p, c, t, cost in _filtered(
                    db.query(
                        RequestLog.provider,
                        func.count(RequestLog.id),
                        func.sum(RequestLog.total_tokens),
                        func.sum(RequestLog.total_cost_usd),
                    )
                ).group_by(RequestLog.provider).all()
            ]

            model_usage = [
                {"model": m, "provider": p, "requests": c, "tokens": int(t or 0), "cost_usd": round(cost or 0.0, 6)}
                for m, p, c, t, cost in _filtered(
                    db.query(
                        RequestLog.model,
                        RequestLog.provider,
                        func.count(RequestLog.id),
                        func.sum(RequestLog.total_tokens),
                        func.sum(RequestLog.total_cost_usd),
                    )
                ).group_by(RequestLog.model, RequestLog.provider).all()
            ]

            # Daily time series (dialect-agnostic: group in Python)
            rows = _filtered(
                db.query(
                    RequestLog.created_at,
                    RequestLog.total_tokens,
                    RequestLog.total_cost_usd,
                    RequestLog.latency_ms,
                )
            ).all()
            buckets: Dict[str, Dict[str, Any]] = {}
            for created_at, tokens, cost, latency in rows:
                day = created_at.strftime("%Y-%m-%d") if created_at else "unknown"
                b = buckets.setdefault(day, {"date": day, "requests": 0, "tokens": 0, "cost_usd": 0.0, "latency_sum": 0.0})
                b["requests"] += 1
                b["tokens"] += tokens or 0
                b["cost_usd"] += cost or 0.0
                b["latency_sum"] += latency or 0.0
            time_series = []
            for day in sorted(buckets):
                b = buckets[day]
                time_series.append({
                    "date": b["date"],
                    "requests": b["requests"],
                    "tokens": b["tokens"],
                    "cost_usd": round(b["cost_usd"], 6),
                    "avg_latency_ms": round(b["latency_sum"] / b["requests"], 1),
                })

            optimized = _filtered(db.query(RequestLog)).filter(RequestLog.optimization_enabled == True).all()  # noqa: E712
            optimization_stats = {
                "optimized_requests": len(optimized),
                "avg_estimated_reduction_percent": round(
                    sum(r.optimization_reduction_percent or 0 for r in optimized) / len(optimized), 2
                ) if optimized else 0.0,
            }

            return {
                "has_data": True,
                "database_available": True,
                "range": time_range,
                "totals": {
                    "requests": total_requests,
                    "total_tokens": int(total_tokens),
                    "input_tokens": int(input_tokens),
                    "output_tokens": int(output_tokens),
                    "total_cost_usd": round(float(total_cost), 6),
                    "avg_latency_ms": round(float(avg_latency), 1),
                    "avg_tokens_per_request": round(int(total_tokens) / total_requests, 1),
                },
                "provider_usage": provider_usage,
                "model_usage": model_usage,
                "time_series": time_series,
                "optimization": optimization_stats,
            }
        except Exception:
            logger.exception("Analytics query failed.")
            return {"has_data": False, "database_available": False, "range": time_range}
        finally:
            try:
                db.close()
            except Exception:
                pass
