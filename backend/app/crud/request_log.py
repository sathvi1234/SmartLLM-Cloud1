import logging
from typing import Any, Dict, List, Optional

from app.db.session import SessionLocal
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

_PREVIEW_LEN = 2000


def record_request(**fields) -> Optional[str]:
    """Persist a completed request. Returns the request id, or None when the
    database is unavailable (the request itself still succeeds)."""
    prompt = fields.pop("prompt", None)
    response = fields.pop("response", None)
    log = RequestLog(
        prompt_preview=(prompt or "")[:_PREVIEW_LEN] or None,
        response_preview=(response or "")[:_PREVIEW_LEN] or None,
        **fields,
    )
    try:
        db = SessionLocal()
        try:
            db.add(log)
            db.commit()
            db.refresh(log)
            return log.id
        finally:
            db.close()
    except Exception:
        logger.exception("Could not record request history (database unavailable?).")
        return None


def list_requests(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = (
            db.query(RequestLog)
            .order_by(RequestLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [r.to_dict() for r in rows]
    finally:
        db.close()


def get_request(request_id: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        row = db.query(RequestLog).filter(RequestLog.id == request_id).first()
        return row.to_dict() if row else None
    finally:
        db.close()
