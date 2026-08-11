"""Centralized model configuration for SmartLLM Cloud.

All model pricing, capability scores and context limits live here.
Pricing is per 1M tokens (USD), sourced from official provider pricing pages.
Do not scatter pricing anywhere else in the codebase.
"""
import asyncio
import time
from typing import Any, Dict, List, Optional

import httpx

from app.ai.router.schemas import ModelProfile
from app.core.config import settings

# ---------------------------------------------------------------------------
# The single source of truth for models SmartLLM can route to.
# quality_score: 1-10 capability estimate, privacy_score: 1-10 (10 = local).
# ---------------------------------------------------------------------------
CATALOG: List[ModelProfile] = [
    ModelProfile(
        provider="openai", model_name="gpt-4o",
        cost_per_1m_prompt=2.50, cost_per_1m_completion=10.00,
        base_latency_ms=500, quality_score=9.5, privacy_score=7.0,
        context_limit=128_000,
    ),
    ModelProfile(
        provider="openai", model_name="gpt-4o-mini",
        cost_per_1m_prompt=0.15, cost_per_1m_completion=0.60,
        base_latency_ms=300, quality_score=8.5, privacy_score=7.0,
        context_limit=128_000,
    ),
    ModelProfile(
        provider="gemini", model_name="gemini-2.5-flash",
        cost_per_1m_prompt=0.30, cost_per_1m_completion=2.50,
        base_latency_ms=450, quality_score=9.0, privacy_score=6.0,
        context_limit=1_048_576,
    ),
    ModelProfile(
        provider="gemini", model_name="gemini-2.5-flash-lite",
        cost_per_1m_prompt=0.10, cost_per_1m_completion=0.40,
        base_latency_ms=300, quality_score=8.0, privacy_score=6.0,
        context_limit=1_048_576,
    ),
    ModelProfile(
        provider="groq", model_name="llama-3.3-70b-versatile",
        cost_per_1m_prompt=0.59, cost_per_1m_completion=0.79,
        base_latency_ms=150, quality_score=8.8, privacy_score=8.0,
        context_limit=128_000,
    ),
    ModelProfile(
        provider="groq", model_name="llama-3.1-8b-instant",
        cost_per_1m_prompt=0.05, cost_per_1m_completion=0.08,
        base_latency_ms=100, quality_score=7.5, privacy_score=8.0,
        context_limit=128_000,
    ),
    ModelProfile(
        provider="ollama", model_name="llama3.1",
        cost_per_1m_prompt=0.0, cost_per_1m_completion=0.0,
        base_latency_ms=1000, quality_score=7.5, privacy_score=10.0,
        context_limit=128_000,
    ),
    # Official xAI Text API pricing for prompts under 200k tokens
    # https://docs.x.ai/developers/models
    ModelProfile(
        provider="xai", model_name="grok-4.5",
        cost_per_1m_prompt=2.00, cost_per_1m_completion=6.00,
        base_latency_ms=400, quality_score=9.7, privacy_score=7.0,
        context_limit=500_000,
    ),
    ModelProfile(
        provider="xai", model_name="grok-4.3",
        cost_per_1m_prompt=1.25, cost_per_1m_completion=2.50,
        base_latency_ms=350, quality_score=9.2, privacy_score=7.0,
        context_limit=1_000_000,
    ),
]


def get_profile(model_name: str, provider: Optional[str] = None) -> Optional[ModelProfile]:
    """Look up a model profile, preferring an exact provider+model match."""
    if provider:
        for p in CATALOG:
            if p.provider == provider.lower() and p.model_name == model_name:
                return p
    for p in CATALOG:
        if p.model_name == model_name:
            return p
    return None


def default_model_for_provider(provider: str) -> Optional[str]:
    for p in CATALOG:
        if p.provider == provider.lower():
            return p.model_name
    return None


# ---------------------------------------------------------------------------
# Provider availability.
# - configured: API key / local config is present (never implies live usability)
# - available: a recent live probe succeeded (usable for AUTO routing)
# ---------------------------------------------------------------------------
_ollama_cache: Dict[str, float] = {"checked_at": 0.0, "available": 0.0}
_OLLAMA_TTL_SECONDS = 30.0

# Live generation probe cache: provider -> {checked_at, usable, reason}
_live_cache: Dict[str, Dict[str, object]] = {}
_LIVE_TTL_SECONDS = 90.0


async def is_ollama_reachable() -> bool:
    now = time.time()
    if now - _ollama_cache["checked_at"] < _OLLAMA_TTL_SECONDS:
        return bool(_ollama_cache["available"])
    reachable = False
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            reachable = resp.status_code == 200
    except Exception:
        reachable = False
    _ollama_cache["checked_at"] = now
    _ollama_cache["available"] = 1.0 if reachable else 0.0
    return reachable


def provider_configured(provider: str) -> bool:
    provider = provider.lower()
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    if provider == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if provider == "groq":
        return bool(settings.GROQ_API_KEY)
    if provider in ("xai", "grok"):
        return bool(settings.XAI_API_KEY)
    if provider == "ollama":
        return bool(settings.OLLAMA_BASE_URL)
    return False


def _api_key_for_provider(provider: str) -> Optional[str]:
    provider = provider.lower()
    raw = {
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "groq": settings.GROQ_API_KEY,
        "xai": settings.XAI_API_KEY,
    }.get(provider)
    if not raw:
        return None
    return raw.strip().strip('"').strip("'")


def _probe_model_for_provider(provider: str) -> Optional[str]:
    """Cheapest catalog model for a short live probe (not for production routing)."""
    candidates = [p for p in CATALOG if p.provider == provider.lower()]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda p: p.cost_per_1m_prompt + p.cost_per_1m_completion,
    ).model_name


def mark_provider_live_result(provider: str, usable: bool, reason: str = "") -> None:
    """Update the live-usability cache (e.g. after a real generate failure)."""
    provider = "xai" if provider.lower() == "grok" else provider.lower()
    _live_cache[provider] = {
        "checked_at": time.time(),
        "usable": bool(usable),
        "reason": reason or ("ok" if usable else "failed"),
    }


async def probe_provider_live(provider: str) -> bool:
    """Return True only if the provider can complete a tiny live generation.

    Results are cached briefly. Configured-but-broken providers (no credits,
    auth failure, bad model, connectivity) are treated as unavailable for AUTO
    routing without removing them from the project.
    """
    provider = "xai" if provider.lower() == "grok" else provider.lower()
    now = time.time()
    cached = _live_cache.get(provider)
    if cached and (now - float(cached["checked_at"])) < _LIVE_TTL_SECONDS:
        return bool(cached["usable"])

    if not provider_configured(provider):
        mark_provider_live_result(provider, False, "not_configured")
        return False

    if provider == "ollama":
        ok = await is_ollama_reachable()
        mark_provider_live_result(provider, ok, "ollama_tags" if ok else "ollama_unreachable")
        return ok

    model = _probe_model_for_provider(provider)
    if not model:
        mark_provider_live_result(provider, False, "no_catalog_model")
        return False

    try:
        # Local import avoids circular imports at module load.
        from app.ai.factory import AIFactory
        from app.ai.schemas import AIRequest, Message, Role

        factory = AIFactory.get_provider(
            provider_name=provider,
            api_key=_api_key_for_provider(provider),
            base_url=settings.OLLAMA_BASE_URL if provider == "ollama" else (
                settings.XAI_BASE_URL if provider == "xai" else None
            ),
        )
        req = AIRequest(
            model=model,
            messages=[Message(role=Role.user, content="ping")],
            temperature=0,
            max_tokens=1,
            timeout=20,
        )
        await factory.run(req)
        mark_provider_live_result(provider, True, "live_ok")
        return True
    except Exception as exc:
        # Never log secrets; keep a short class/status reason only.
        reason = exc.__class__.__name__
        detail = getattr(exc, "message", "") or str(exc)
        detail_l = detail.lower()
        if "credit" in detail_l or "quota" in detail_l or "insufficient" in detail_l:
            reason = "no_credits"
        elif "auth" in detail_l or "api key" in detail_l or "unauthorized" in detail_l:
            reason = "auth_failed"
        elif "404" in detail_l or "not found" in detail_l or "no longer available" in detail_l:
            reason = "model_unavailable"
        mark_provider_live_result(provider, False, reason)
        return False


async def get_provider_status() -> Dict[str, Dict[str, Any]]:
    """Returns {provider: {configured, available, live_reason}} for all providers.

    configured = key/config present
    available  = live probe succeeded (AUTO routing uses this list only)
    """
    cloud = ("openai", "gemini", "groq", "xai")
    # Probe configured providers in parallel so AUTO is not blocked by slow failures.
    await asyncio.gather(
        *[probe_provider_live(p) for p in cloud if provider_configured(p)],
        return_exceptions=True,
    )

    status: Dict[str, Dict[str, Any]] = {}
    for provider in cloud:
        configured = provider_configured(provider)
        if configured:
            cached = _live_cache.get(provider, {})
            status[provider] = {
                "configured": True,
                "available": bool(cached.get("usable", False)),
                "live_reason": str(cached.get("reason", "")),
            }
        else:
            status[provider] = {
                "configured": False,
                "available": False,
                "live_reason": "not_configured",
            }
    ollama_ok = await is_ollama_reachable()
    status["ollama"] = {
        "configured": provider_configured("ollama"),
        "available": ollama_ok,
        "live_reason": "ok" if ollama_ok else "ollama_unreachable",
    }
    return status


async def get_available_providers() -> List[str]:
    """Providers safe for SmartLLM AUTO routing (live-usable only)."""
    status = await get_provider_status()
    return [name for name, s in status.items() if s["available"]]
