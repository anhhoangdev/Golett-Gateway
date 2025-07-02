"""Token-based pruning utility for ContextForge."""
from __future__ import annotations

from typing import List

from golett_core.schemas.memory import MemoryItem

try:
    import tiktoken
    _ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")
except ImportError:
    # Fallback – rough approximation using whitespace split
    _ENCODER = None


def _count_tokens(text: str) -> int:
    if _ENCODER:
        return len(_ENCODER.encode(text))
    return len(text.split())


class TokenBudgeter:
    """Greedy selection under a token budget (default 3000)."""

    def prune(self, items: List[MemoryItem], budget_tokens: int = 3000) -> List[MemoryItem]:
        selected: List[MemoryItem] = []
        total = 0
        for itm in items:
            total += _count_tokens(itm.content)
            if total > budget_tokens:
                break
            selected.append(itm)
        return selected 