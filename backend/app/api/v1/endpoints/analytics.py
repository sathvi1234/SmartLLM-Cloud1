from typing import Any, Dict

from fastapi import APIRouter, Query

from app.services.analytics import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/overview", response_model=Dict[str, Any])
def get_analytics_overview(range: str = Query("all")):
    if range not in {"today", "7d", "30d", "all"}:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid range. Use today, 7d, 30d, or all.")
    """Real aggregated metrics from stored requests. Returns has_data=False
    (never fabricated numbers) when nothing has been recorded yet."""
    return analytics_service.get_overview(time_range=range)
