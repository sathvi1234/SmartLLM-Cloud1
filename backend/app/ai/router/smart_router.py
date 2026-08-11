from typing import Dict, List, Optional

from app.ai.model_catalog import CATALOG
from app.ai.router.schemas import ModelProfile, RoutingResult
from app.ai.router.token_estimator import TokenEstimator
from app.ai.router.evaluators.cost import CostEvaluator
from app.ai.router.evaluators.latency import LatencyEvaluator
from app.ai.router.evaluators.quality import QualityEvaluator
from app.ai.router.evaluators.privacy import PrivacyEvaluator

# Re-exported for modules that historically imported CATALOG from here.
__all__ = ["SmartModelRouter", "CATALOG"]

# Public optimization modes -> internal weighting profiles
MODE_ALIASES = {
    "cost": "cost",
    "speed": "latency",
    "latency": "latency",
    "quality": "quality",
    "privacy": "privacy",
    "balanced": "balanced",
}


class SmartModelRouter:
    def __init__(self):
        self.cost_evaluator = CostEvaluator()
        self.latency_evaluator = LatencyEvaluator()
        self.quality_evaluator = QualityEvaluator()
        self.privacy_evaluator = PrivacyEvaluator()

    def route(
        self,
        prompt: str,
        optimize_for: str = "balanced",
        min_privacy: float = 0.0,
        allowed_providers: Optional[List[str]] = None,
        expected_output_tokens: Optional[int] = None,
        task_summary: Optional[str] = None,
    ) -> RoutingResult:
        mode = MODE_ALIASES.get(optimize_for.lower(), "balanced")
        estimated_tokens = TokenEstimator.estimate(prompt)
        weights = self._get_weights(mode)

        candidates: List[ModelProfile] = []
        for profile in CATALOG:
            if allowed_providers is not None and profile.provider not in allowed_providers:
                continue
            if profile.privacy_score < min_privacy:
                continue
            # Leave headroom in the context window for the completion
            needed = estimated_tokens + (expected_output_tokens or 0)
            if needed > profile.context_limit:
                continue
            candidates.append(profile)

        if not candidates:
            raise ValueError(
                "No model satisfied the routing constraints. "
                "Check that at least one provider is configured and available."
            )

        best_profile: Optional[ModelProfile] = None
        best_score = -1.0
        best_components: Dict[str, float] = {}

        for profile in candidates:
            cost_score = self.cost_evaluator.evaluate(profile, estimated_tokens)
            latency_score = self.latency_evaluator.evaluate(profile, estimated_tokens)
            quality_score = self.quality_evaluator.evaluate(profile, estimated_tokens)
            privacy_score = self.privacy_evaluator.evaluate(profile, estimated_tokens)

            total_score = (
                (cost_score * weights["cost"])
                + (latency_score * weights["latency"])
                + (quality_score * weights["quality"])
                + (privacy_score * weights["privacy"])
            )

            if total_score > best_score:
                best_score = total_score
                best_profile = profile
                best_components = {
                    "cost": cost_score,
                    "latency": latency_score,
                    "quality": quality_score,
                    "privacy": privacy_score,
                }

        profile = best_profile
        est_cost = self.cost_evaluator.estimate_cost(profile, estimated_tokens)
        est_latency = self.latency_evaluator.estimate_latency(profile, estimated_tokens)

        reasoning = self._build_reasoning(
            profile=profile,
            mode=optimize_for.lower(),
            weights=weights,
            components=best_components,
            candidate_count=len(candidates),
            est_cost=est_cost,
            est_latency=est_latency,
            task_summary=task_summary,
        )

        return RoutingResult(
            provider=profile.provider,
            model_name=profile.model_name,
            estimated_tokens=estimated_tokens,
            estimated_cost=est_cost,
            estimated_latency_ms=est_latency,
            quality_score=best_components["quality"],
            privacy_score=best_components["privacy"],
            total_score=best_score,
            reasoning=reasoning,
        )

    def _build_reasoning(
        self,
        profile: ModelProfile,
        mode: str,
        weights: Dict[str, float],
        components: Dict[str, float],
        candidate_count: int,
        est_cost: float,
        est_latency: int,
        task_summary: Optional[str],
    ) -> str:
        priority = max(weights, key=weights.get)
        parts = [
            f"{mode.capitalize()} mode prioritizes {priority} "
            f"(weights: cost {int(weights['cost']*100)}%, speed {int(weights['latency']*100)}%, "
            f"quality {int(weights['quality']*100)}%, privacy {int(weights['privacy']*100)}%).",
            f"{profile.model_name} ({profile.provider}) scored highest of {candidate_count} available candidate(s) "
            f"with capability {profile.quality_score}/10, "
            f"estimated cost ${est_cost:.6f} and estimated latency ~{est_latency}ms for this prompt.",
        ]
        if profile.cost_per_1m_prompt == 0:
            parts.append("It runs locally, so token cost is $0.")
        if task_summary:
            parts.append(f"Task analysis: {task_summary}.")
        return " ".join(parts)

    def _get_weights(self, optimize_for: str) -> Dict[str, float]:
        if optimize_for == "cost":
            return {"cost": 0.6, "latency": 0.1, "quality": 0.2, "privacy": 0.1}
        elif optimize_for == "latency":
            return {"cost": 0.1, "latency": 0.6, "quality": 0.2, "privacy": 0.1}
        elif optimize_for == "quality":
            return {"cost": 0.1, "latency": 0.1, "quality": 0.7, "privacy": 0.1}
        elif optimize_for == "privacy":
            return {"cost": 0.1, "latency": 0.1, "quality": 0.1, "privacy": 0.7}
        else:  # balanced
            return {"cost": 0.25, "latency": 0.25, "quality": 0.4, "privacy": 0.1}
