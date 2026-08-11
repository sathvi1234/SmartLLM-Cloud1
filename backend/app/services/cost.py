"""Centralized cost calculation from actual token usage.

input_cost  = input_tokens  x input_price_per_token
output_cost = output_tokens x output_price_per_token
total_cost  = input_cost + output_cost

Pricing comes exclusively from the model catalog. If a model is not in the
catalog we report pricing as unavailable instead of inventing a number.
"""
from typing import Any, Dict, Optional

from app.ai.model_catalog import get_profile


def compute_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> Dict[str, Any]:
    profile = get_profile(model, provider)
    if profile is None or not profile.pricing_known:
        return {
            "input_cost_usd": None,
            "output_cost_usd": None,
            "total_cost_usd": None,
            "pricing_available": False,
            "pricing_note": f"Pricing unavailable for {provider}/{model}.",
        }

    input_cost = (input_tokens / 1_000_000) * profile.cost_per_1m_prompt
    output_cost = (output_tokens / 1_000_000) * profile.cost_per_1m_completion
    return {
        "input_cost_usd": round(input_cost, 8),
        "output_cost_usd": round(output_cost, 8),
        "total_cost_usd": round(input_cost + output_cost, 8),
        "pricing_available": True,
        "pricing_note": (
            f"${profile.cost_per_1m_prompt}/1M input, "
            f"${profile.cost_per_1m_completion}/1M output ({provider}/{profile.model_name})"
        ),
    }
