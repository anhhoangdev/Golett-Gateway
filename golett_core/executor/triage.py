from __future__ import annotations

from enum import Enum

__all__ = [
    "Intent",
    "IntentClassifier",
]


class Intent(str, Enum):
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    CONVERSATIONAL = "CONVERSATIONAL"


class IntentClassifier:
    """Cheap heuristic / placeholder until an LLM classifier is plugged in."""

    async def classify(self, text: str) -> Intent:  # noqa: D401
        """Return intent based on simple heuristics (replace w/ LLM later)."""
        if "?" in text or any(keyword in text.lower() for keyword in ["how", "what", "why", "when", "where"]):
            return Intent.KNOWLEDGE_QUERY
        return Intent.CONVERSATIONAL 