"""Conservative, rule-based prompt optimization.

Removes safe redundancies (whitespace, polite filler, exact duplicate
sentences) while preserving meaning. Code blocks, inline code, URLs and
structured data are never modified. Token counts are estimates from the
tokenizer, not measured provider usage.
"""
import json
import re
from typing import Any, Dict, List, Tuple

from app.ai.router.token_estimator import TokenEstimator

_PLACEHOLDER = "\x00PROT{}\x00"

# Patterns whose matches must never be altered
_PROTECTED_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),          # fenced code blocks
    re.compile(r"`[^`\n]+`"),                     # inline code
    re.compile(r"https?://\S+"),                  # URLs
    re.compile(r"\{[^{}]*\}"),                    # inline JSON-ish objects
]

# Conservative filler removals. Each entry: (name, pattern, replacement)
_FILLER_RULES: List[Tuple[str, re.Pattern, str]] = [
    ("polite_request", re.compile(r"\b(?:could|can|would) you (?:please\s+)?", re.IGNORECASE), ""),
    ("polite_please", re.compile(r"\bplease\s+", re.IGNORECASE), ""),
    ("polite_kindly", re.compile(r"\bkindly\s+", re.IGNORECASE), ""),
    ("polite_thanks", re.compile(r"[,.]?\s*thank(?:s| you)(?: in advance| so much)?\s*[.!]?", re.IGNORECASE), ""),
    ("indirect_request", re.compile(r"\bI(?:'d| would) (?:really\s+)?like you to\s+", re.IGNORECASE), ""),
    ("indirect_want", re.compile(r"\bI (?:want|need) you to\s+", re.IGNORECASE), ""),
    ("hedging", re.compile(r"\bif (?:possible|you can|you don't mind),?\s*", re.IGNORECASE), ""),
]

_SQL_LINE = re.compile(r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH)\b", re.IGNORECASE)
_CODE_LINE = re.compile(r"^\s*(def |class |import |from |function |const |let |var |return |if\s*\(|for\s*\()")


def _looks_structured(prompt: str) -> bool:
    """True when the prompt is predominantly code/SQL/JSON and must not be touched."""
    stripped = prompt.strip()
    if stripped.startswith(("{", "[")):
        try:
            json.loads(stripped)
            return True
        except (ValueError, TypeError):
            pass
    lines = [ln for ln in stripped.splitlines() if ln.strip()]
    if not lines:
        return False
    codeish = sum(1 for ln in lines if _SQL_LINE.match(ln) or _CODE_LINE.match(ln))
    return codeish / len(lines) > 0.4


class SafePromptOptimizer:
    def optimize(self, prompt: str) -> Dict[str, Any]:
        tokens_before = TokenEstimator.estimate(prompt)
        base = {
            "original_prompt": prompt,
            "optimized_prompt": prompt,
            "estimated_tokens_before": tokens_before,
            "estimated_tokens_after": tokens_before,
            "reduction_percent": 0.0,
            "techniques_applied": [],
            "optimization_applied": False,
            "note": "Token counts are tokenizer estimates, not measured provider usage.",
        }

        if "[immutable]" in prompt.lower():
            base["note"] = "Prompt marked immutable; left unchanged."
            return base
        if _looks_structured(prompt):
            base["note"] = "Prompt is predominantly code/SQL/JSON; left unchanged for safety."
            return base

        # Shield protected segments behind placeholders
        protected: List[str] = []
        text = prompt
        for pattern in _PROTECTED_PATTERNS:
            def _stash(match: re.Match) -> str:
                protected.append(match.group(0))
                return _PLACEHOLDER.format(len(protected) - 1)
            text = pattern.sub(_stash, text)

        techniques: List[str] = []

        # 1. Remove redundant polite/filler phrasing
        for name, pattern, repl in _FILLER_RULES:
            new_text = pattern.sub(repl, text)
            if new_text != text:
                techniques.append(name)
                text = new_text

        # 2. Collapse repeated consecutive words ("write write a function")
        deduped = re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", text, flags=re.IGNORECASE)
        if deduped != text:
            techniques.append("repeated_word_removal")
            text = deduped

        # 3. Remove exact duplicate sentences (normalized comparison)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        seen = set()
        kept = []
        for s in sentences:
            key = re.sub(r"\s+", " ", s).strip().lower()
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            kept.append(s)
        if len(kept) < len(sentences):
            techniques.append("duplicate_sentence_removal")
        text = " ".join(kept)

        # 4. Collapse excessive whitespace
        collapsed = re.sub(r"[ \t]{2,}", " ", text)
        collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
        collapsed = re.sub(r"[ \t]+\n", "\n", collapsed).strip()
        if collapsed != text:
            techniques.append("whitespace_collapse")
        text = collapsed

        # Capitalize first letter if filler removal left it lowercase
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Restore protected segments
        for i, segment in enumerate(protected):
            text = text.replace(_PLACEHOLDER.format(i), segment)

        tokens_after = TokenEstimator.estimate(text)
        # Never return an "optimization" that grows the prompt or empties it
        if not text.strip() or tokens_after >= tokens_before:
            return base

        reduction = round((tokens_before - tokens_after) / tokens_before * 100, 2) if tokens_before else 0.0
        return {
            "original_prompt": prompt,
            "optimized_prompt": text,
            "estimated_tokens_before": tokens_before,
            "estimated_tokens_after": tokens_after,
            "reduction_percent": reduction,
            "techniques_applied": techniques,
            "optimization_applied": True,
            "note": "Token counts are tokenizer estimates, not measured provider usage.",
        }
