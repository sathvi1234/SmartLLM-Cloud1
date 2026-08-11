from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.cache import SemanticCache
from app.ai.exceptions import AIProviderException
from app.ai.factory import AIFactory
from app.ai.model_catalog import (
    CATALOG,
    default_model_for_provider,
    get_available_providers,
    get_provider_status,
    mark_provider_live_result,
)
from app.ai.router.analyzer import PromptAnalyzer
from app.ai.router.cost_predictor import CostPredictionEngine
from app.ai.router.smart_router import SmartModelRouter
from app.ai.router.token_estimator import TokenEstimator
from app.ai.safe_optimizer import SafePromptOptimizer
from app.ai.schemas import AIRequest, AIResponse, Message, Role
from app.core.config import settings
from app.crud import request_log as request_log_crud
from app.services.cost import compute_cost

router = APIRouter()
analyzer = PromptAnalyzer()
safe_optimizer = SafePromptOptimizer()
smart_router = SmartModelRouter()
cost_predictor = CostPredictionEngine()
semantic_cache = SemanticCache()

VALID_PROVIDERS = {"openai", "gemini", "groq", "xai", "ollama"}
VALID_MODES = {"cost", "speed", "balanced", "quality"}

_KEY_ENV_NAMES = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "xai": "XAI_API_KEY",
}


def _api_key_for(provider: str) -> Optional[str]:
    raw = {
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "groq": settings.GROQ_API_KEY,
        "xai": settings.XAI_API_KEY,
    }.get(provider)
    if not raw:
        return None
    return raw.strip().strip('"').strip("'")


def _base_url_for(provider: str) -> Optional[str]:
    if provider == "ollama":
        return settings.OLLAMA_BASE_URL
    if provider == "xai":
        return settings.XAI_BASE_URL
    return None


async def _execute(provider_name: str, model: str, prompt: str, max_tokens: int = 2048) -> AIResponse:
    provider_name = provider_name.lower()
    if provider_name == "grok":
        provider_name = "xai"
    if provider_name not in VALID_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Invalid provider '{provider_name}'. Valid: {sorted(VALID_PROVIDERS)}")

    api_key = _api_key_for(provider_name)
    if provider_name != "ollama" and not api_key:
        env_name = _KEY_ENV_NAMES.get(provider_name, "the provider API key")
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider_name}' is not configured. Set {env_name} in backend/.env.",
        )

    provider = AIFactory.get_provider(
        provider_name=provider_name,
        api_key=api_key,
        base_url=_base_url_for(provider_name),
    )
    ai_req = AIRequest(
        model=model,
        messages=[Message(role=Role.user, content=prompt)],
        temperature=0.7,
        max_tokens=max_tokens,
        timeout=90,
    )
    return await provider.run(ai_req)


def _usage_and_cost(res: AIResponse) -> Dict[str, Any]:
    cost = compute_cost(res.provider, res.model, res.usage.prompt_tokens, res.usage.completion_tokens)
    return {
        "content": res.content,
        "provider": res.provider,
        "model": res.model,
        "usage": res.usage.model_dump(),
        "latency_ms": round(res.latency_ms, 1),
        "cost": cost,
    }


# ---------------------------------------------------------------------------
# Analysis / optimization utilities (kept from the existing API)
# ---------------------------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str


@router.post("/analyze", response_model=Dict[str, Any])
def analyze_prompt(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    return analyzer.analyze(request.prompt)


class OptimizeRequest(BaseModel):
    prompt: str


@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_prompt(request: OptimizeRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    return safe_optimizer.optimize(request.prompt)


class CostPredictionRequest(BaseModel):
    prompt: str
    selected_llm: str
    provider: Optional[str] = None


@router.post("/predict-cost", response_model=Dict[str, Any])
def predict_cost(request: CostPredictionRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    return cost_predictor.predict(request.prompt, request.selected_llm, request.provider)


class CountTokensRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None


@router.post("/count-tokens", response_model=Dict[str, Any])
def count_tokens(request: CountTokensRequest):
    if not request.prompt.strip():
        return {"tokens": 0, "provider": request.provider, "model_name": request.model_name}
    tokens = TokenEstimator.estimate(
        prompt=request.prompt,
        provider=request.provider,
        model_name=request.model_name,
        api_key=request.api_key,
    )
    return {"tokens": tokens, "provider": request.provider, "model_name": request.model_name}


# ---------------------------------------------------------------------------
# Direct generation (baseline). Cost is computed from ACTUAL usage tokens.
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    record: bool = True
    source: str = "playground"


@router.post("/generate", response_model=Dict[str, Any])
async def generate_prompt(request: GenerateRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    res = await _execute(request.provider, request.model_name, request.prompt, request.max_tokens)
    payload = _usage_and_cost(res)

    request_id = None
    if request.record:
        request_id = request_log_crud.record_request(
            prompt=request.prompt,
            response=res.content,
            provider=res.provider,
            model=res.model,
            routing_mode="direct",
            source=request.source,
            input_tokens=res.usage.prompt_tokens,
            output_tokens=res.usage.completion_tokens,
            total_tokens=res.usage.total_tokens,
            latency_ms=res.latency_ms,
            input_cost_usd=payload["cost"]["input_cost_usd"],
            output_cost_usd=payload["cost"]["output_cost_usd"],
            total_cost_usd=payload["cost"]["total_cost_usd"],
            pricing_available=payload["cost"]["pricing_available"],
            optimization_enabled=False,
            optimization_reduction_percent=0.0,
        )
    payload["request_id"] = request_id
    return payload


# ---------------------------------------------------------------------------
# SmartLLM pipeline: analyze -> optimize -> route -> generate -> measure
# ---------------------------------------------------------------------------
class SmartGenerateRequest(BaseModel):
    prompt: str
    mode: str = "balanced"                 # cost | speed | balanced | quality
    provider: str = "auto"                 # auto or a specific provider
    model_name: Optional[str] = None       # optional specific model
    optimize: bool = True
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    record: bool = True
    source: str = "playground"


async def _run_smart_pipeline(request: SmartGenerateRequest) -> Dict[str, Any]:
    mode = request.mode.lower()
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode '{request.mode}'. Valid: {sorted(VALID_MODES)}")

    # 1. Analyze
    features = analyzer.features(request.prompt)

    # 2. Optimize (safe, rule-based)
    optimization = safe_optimizer.optimize(request.prompt) if request.optimize else None
    final_prompt = optimization["optimized_prompt"] if optimization else request.prompt

    # 3. Route
    predicted_output, _ = cost_predictor._predict_output_tokens(final_prompt, features["estimated_tokens"])
    if request.provider == "auto":
        # Only providers that pass a live usability probe (not merely configured).
        allowed = await get_available_providers()
        if not allowed:
            raise HTTPException(
                status_code=503,
                detail=(
                    "No AI provider is currently usable for live generation. "
                    "Configured keys may lack credits, fail authentication, or be unreachable. "
                    "Check Provider Health and ensure at least one provider can complete a request."
                ),
            )
        task_summary = f"intent {', '.join(features['intent'])}; difficulty {features['difficulty']}"
        try:
            routing = smart_router.route(
                final_prompt,
                optimize_for=mode,
                allowed_providers=allowed,
                expected_output_tokens=predicted_output,
                task_summary=task_summary,
            )
        except ValueError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        selected_provider = routing.provider
        selected_model = routing.model_name
        routing_info = {
            "selected_provider": selected_provider,
            "selected_model": selected_model,
            "mode": mode,
            "reason": (
                f"{routing.reasoning} "
                f"AUTO candidates (live-usable): {', '.join(allowed)}."
            ),
            "estimated_cost": round(routing.estimated_cost, 6),
            "estimated_latency_ms": routing.estimated_latency_ms,
            "auto_routed": True,
            "auto_candidates": allowed,
        }
    else:
        selected_provider = request.provider.lower()
        if selected_provider not in VALID_PROVIDERS:
            raise HTTPException(status_code=400, detail=f"Invalid provider '{request.provider}'.")
        selected_model = request.model_name or default_model_for_provider(selected_provider)
        if not selected_model:
            raise HTTPException(status_code=400, detail=f"No model specified or known for provider '{selected_provider}'.")
        routing_info = {
            "selected_provider": selected_provider,
            "selected_model": selected_model,
            "mode": mode,
            "reason": f"Provider/model manually selected by user ({selected_provider}/{selected_model}); router bypassed.",
            "estimated_cost": None,
            "estimated_latency_ms": None,
            "auto_routed": False,
        }

    # 4. Generate (real provider call)
    try:
        res = await _execute(selected_provider, selected_model, final_prompt, request.max_tokens)
        mark_provider_live_result(selected_provider, True, "generate_ok")
    except Exception:
        # Keep AUTO from repeatedly selecting a broken provider until the next probe window.
        if request.provider == "auto":
            mark_provider_live_result(selected_provider, False, "generate_failed")
        raise

    # 5. Real cost from actual usage tokens
    payload = _usage_and_cost(res)

    reduction = optimization["reduction_percent"] if optimization else 0.0
    request_id = None
    if request.record:
        request_id = request_log_crud.record_request(
            prompt=request.prompt,
            response=res.content,
            provider=res.provider,
            model=res.model,
            routing_mode=mode,
            source=request.source,
            input_tokens=res.usage.prompt_tokens,
            output_tokens=res.usage.completion_tokens,
            total_tokens=res.usage.total_tokens,
            latency_ms=res.latency_ms,
            input_cost_usd=payload["cost"]["input_cost_usd"],
            output_cost_usd=payload["cost"]["output_cost_usd"],
            total_cost_usd=payload["cost"]["total_cost_usd"],
            pricing_available=payload["cost"]["pricing_available"],
            optimization_enabled=bool(request.optimize and optimization and optimization["optimization_applied"]),
            optimization_reduction_percent=reduction,
        )

    payload.update({
        "request_id": request_id,
        "analysis": features,
        "routing": routing_info,
        "optimization": optimization,
    })
    return payload


@router.post("/smart-generate", response_model=Dict[str, Any])
async def smart_generate(request: SmartGenerateRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    return await _run_smart_pipeline(request)


# ---------------------------------------------------------------------------
# Benchmark: Direct LLM vs SmartLLM on the same prompt, real measurements only
# ---------------------------------------------------------------------------
class BenchmarkRequest(BaseModel):
    prompt: str
    # Empty / "auto" = pick the first configured provider (OpenAI preferred if available).
    baseline_provider: str = "auto"
    baseline_model: Optional[str] = None
    mode: str = "balanced"
    optimize: bool = True
    max_tokens: int = Field(default=2048, ge=1, le=8192)


def _pct_change(direct: Optional[float], smart: Optional[float]) -> Optional[float]:
    """Percent change from Direct to SmartLLM. Negative = SmartLLM is lower."""
    if direct is None or smart is None or direct == 0:
        return None
    return round((smart - direct) / direct * 100, 2)


async def _resolve_benchmark_baseline(
    baseline_provider: str,
    baseline_model: Optional[str],
) -> tuple[str, str]:
    """Pick a configured Direct-LLM baseline. Does not require OpenAI specifically."""
    available = await get_available_providers()
    if not available:
        raise HTTPException(
            status_code=503,
            detail="No AI provider is currently usable for the Direct LLM baseline. "
                   "Configured keys may lack credits or fail live generation. "
                   "Ensure at least one provider (e.g. Groq) can complete a request.",
        )

    provider = (baseline_provider or "auto").lower()
    if provider in ("", "auto"):
        # Prefer OpenAI, then Groq (primary free/live test path), then others.
        for preferred in ("openai", "groq", "xai", "gemini", "ollama"):
            if preferred in available:
                provider = preferred
                break
        else:
            provider = available[0]
    elif provider == "grok":
        provider = "xai"

    if provider not in available:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Provider '{provider}' is not usable for the Direct LLM baseline. "
                f"Live-usable baseline providers: {', '.join(available)}. "
                f"Select one of these in Benchmark, or fix {_KEY_ENV_NAMES.get(provider, 'the provider API key')} / credits."
            ),
        )

    model = baseline_model or default_model_for_provider(provider)
    if not model:
        raise HTTPException(
            status_code=400,
            detail=f"No model specified or known for baseline provider '{provider}'.",
        )
    return provider, model


@router.post("/benchmark", response_model=Dict[str, Any])
async def run_benchmark(request: BenchmarkRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    baseline_provider, baseline_model = await _resolve_benchmark_baseline(
        request.baseline_provider,
        request.baseline_model,
    )

    # A. Direct LLM: raw prompt straight to the selected baseline model
    direct_res = await _execute(baseline_provider, baseline_model, request.prompt, request.max_tokens)
    direct = _usage_and_cost(direct_res)
    direct["baseline"] = {
        "provider": baseline_provider,
        "model": baseline_model,
        "requested_provider": request.baseline_provider,
        "requested_model": request.baseline_model,
    }
    direct["request_id"] = request_log_crud.record_request(
        prompt=request.prompt,
        response=direct_res.content,
        provider=direct_res.provider,
        model=direct_res.model,
        routing_mode="direct",
        source="benchmark_direct",
        input_tokens=direct_res.usage.prompt_tokens,
        output_tokens=direct_res.usage.completion_tokens,
        total_tokens=direct_res.usage.total_tokens,
        latency_ms=direct_res.latency_ms,
        input_cost_usd=direct["cost"]["input_cost_usd"],
        output_cost_usd=direct["cost"]["output_cost_usd"],
        total_cost_usd=direct["cost"]["total_cost_usd"],
        pricing_available=direct["cost"]["pricing_available"],
        optimization_enabled=False,
        optimization_reduction_percent=0.0,
    )

    # B. SmartLLM: analyzer -> optimizer -> router -> selected model (unchanged)
    smart = await _run_smart_pipeline(SmartGenerateRequest(
        prompt=request.prompt,
        mode=request.mode,
        provider="auto",
        optimize=request.optimize,
        max_tokens=request.max_tokens,
        record=True,
        source="benchmark_smart",
    ))

    comparison = {
        "token_change_percent": _pct_change(
            direct["usage"]["total_tokens"], smart["usage"]["total_tokens"]
        ),
        "cost_change_percent": _pct_change(
            direct["cost"]["total_cost_usd"], smart["cost"]["total_cost_usd"]
        ),
        "latency_change_percent": _pct_change(direct["latency_ms"], smart["latency_ms"]),
        "note": "Negative values mean SmartLLM used/spent less than Direct LLM. "
                "All values are computed from this run's real measurements.",
    }

    return {
        "direct": direct,
        "smart": smart,
        "baseline": {
            "provider": baseline_provider,
            "model": baseline_model,
            "label": f"{baseline_provider}/{baseline_model}",
        },
        "comparison": comparison,
        "formulas": {
            "cost": "input_cost = input_tokens x input_price_per_token; "
                    "output_cost = output_tokens x output_price_per_token; "
                    "total_cost = input_cost + output_cost (official per-1M-token pricing from the model catalog)",
            "change_percent": "(smartllm_value - direct_value) / direct_value x 100",
            "latency": "Wall-clock time of the provider API call, measured server-side in milliseconds",
            "tokens": "Actual usage reported by the provider API response",
        },
    }


# ---------------------------------------------------------------------------
# Model catalog + request history
# ---------------------------------------------------------------------------
@router.get("/models", response_model=Dict[str, Any])
async def list_models():
    status = await get_provider_status()
    models = []
    for p in CATALOG:
        s = status.get(p.provider, {"configured": False, "available": False})
        models.append({
            "provider": p.provider,
            "model": p.model_name,
            "input_price_per_1m": p.cost_per_1m_prompt,
            "output_price_per_1m": p.cost_per_1m_completion,
            "capability_score": p.quality_score,
            "privacy_score": p.privacy_score,
            "context_limit": p.context_limit,
            "configured": s["configured"],
            "available": s["available"],
        })
    return {"models": models, "providers": status}


@router.get("/requests", response_model=Dict[str, Any])
def list_request_history(limit: int = 50, offset: int = 0):
    try:
        items = request_log_crud.list_requests(limit=min(limit, 200), offset=offset)
        return {"items": items, "database_available": True}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable; request history cannot be read.")


@router.get("/requests/{request_id}", response_model=Dict[str, Any])
def get_request_detail(request_id: str):
    try:
        item = request_log_crud.get_request(request_id)
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable; request history cannot be read.")
    if not item:
        raise HTTPException(status_code=404, detail="Request not found.")
    return item


# ---------------------------------------------------------------------------
# Semantic cache endpoints (existing functionality, unchanged)
# ---------------------------------------------------------------------------
class CacheCheckRequest(BaseModel):
    prompt: str


class CacheSetRequest(BaseModel):
    prompt: str
    response: str
    tokens: int
    cost_usd: float
    latency_ms: int


@router.post("/cache/check", response_model=Dict[str, Any])
async def check_cache(request: CacheCheckRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    result = await semantic_cache.get(request.prompt)
    if result:
        return {"hit": True, "data": result}
    return {"hit": False}


@router.post("/cache/set", response_model=Dict[str, Any])
async def set_cache(request: CacheSetRequest):
    await semantic_cache.set(
        prompt=request.prompt,
        response=request.response,
        tokens=request.tokens,
        cost_usd=request.cost_usd,
        latency_ms=request.latency_ms,
    )
    return {"message": "Cached successfully"}


@router.get("/cache/stats", response_model=Dict[str, Any])
def get_cache_stats():
    return semantic_cache.get_statistics()
