from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.dependencies import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check DB connectivity
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "degraded", "db": "disconnected", "details": str(e)}
