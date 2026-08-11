from fastapi import APIRouter

from app.ai.model_catalog import get_provider_status

router = APIRouter()


@router.get("/")
async def get_providers():
    """Health/configuration status per provider.

    configured = key/config present
    available  = recent live generation probe succeeded (AUTO routing uses this)
    API keys are never returned.
    """
    status = await get_provider_status()
    result = []
    for name, s in status.items():
        configured = bool(s["configured"])
        available = bool(s["available"])
        if available:
            health = "ok"
        elif not configured:
            health = "missing_key"
        else:
            # Key present but live probe failed (credits, auth, model, connectivity)
            health = str(s.get("live_reason") or "unreachable")
        result.append({
            "name": name,
            "configured": configured,
            "available": available,
            "health_status": health,
        })
    return result
