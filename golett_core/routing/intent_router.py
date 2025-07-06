from __future__ import annotations

"""IntentRouter – ultra-lightweight heuristic that decides which agent chain
should handle a given user query.

The router returns either:

* ``"relational"`` – the query is about relationships between entities.
* ``"default"`` – fallback handled by the standard RAG flow.

In production this could be replaced by an LLM classifier but simple heuristics
are usually good enough for a first cut.
"""

import re
from typing import Literal

# Interface contract
from golett_core.interfaces import RouterInterface

# Keep Intent alias for external import convenience
Intent = Literal["relational", "default"]

_RELATIONAL_PATTERNS = re.compile(
    r"\b(relationship|related to|connected to|between|link|owns|part of|parent|child)\b",
    flags=re.IGNORECASE,
)

# pylint: disable=too-few-public-methods
class IntentRouter(RouterInterface):
    """Rule-based router with O(1) latency."""

    def classify(self, query: str) -> Intent:  # noqa: D401
        """Return the intent label for *query*."""
        if _RELATIONAL_PATTERNS.search(query):
            return "relational"
        return "default" 