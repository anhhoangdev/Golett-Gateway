from __future__ import annotations

"""Definitions for crew specifications that the MasterAgent can route to.

A CrewSpec encapsulates the minimal information required by CrewFactory
in order to materialise a concrete crew (agents, tasks, tools, etc.).
The spec purposefully keeps a very small surface area so that new crews
can be registered without touching the core orchestration logic – simply
instantiate a CrewSpec and add it to the registry consumed by the
:class:`MasterAgent`.
"""

from dataclasses import dataclass
from typing import Callable, List

__all__ = [
    "CrewSpec",
    "default_specs",
    "register_spec",
]


@dataclass(frozen=True, slots=True)
class CrewSpec:
    """A minimal declaration of a specialised crew.

    Parameters
    ----------
    name:
        Logical identifier (must be unique).
    description:
        Human-readable blurb shown in logs / analytics.
    match_fn:
        A synchronous predicate that returns ``True`` if the incoming
        *user_message* is deemed to belong to this spec.  The first spec
        whose *match_fn* returns ``True`` will be selected by the
        default :class:`~golett_core.executor.master_agent.MasterAgent`
        routing logic.
    requires_knowledge:
        Indicates whether the crew requires knowledge to perform its tasks.
    """

    name: str
    description: str
    match_fn: Callable[[str], bool]
    requires_knowledge: bool = False

    # Developers might want to attach additional rich metadata here in
    # the future (e.g., required tools); keep the dataclass flexible.


# ---------------------------------------------------------------------------
# Built-in example specs -----------------------------------------------------
# ---------------------------------------------------------------------------

def _is_knowledge_query(message: str) -> bool:  # noqa: D401
    """Very naive heuristic – replace with RAG classifier or fine-tuned LLM."""
    interrogatives = ["how", "what", "why", "when", "where", "?", "explain", "tell me"]
    lowered = message.lower()
    return any(word in lowered for word in interrogatives)


def _always(_msg: str) -> bool:  # noqa: D401
    return True


KNOWLEDGE_QA_CREW = CrewSpec(
    name="knowledge_rag",
    description="Retrieval-augmented answering crew for factual / knowledge-based queries.",
    match_fn=_is_knowledge_query,
    requires_knowledge=True,
)

_CONVERSATION_CREW = CrewSpec(
    name="general_chat",
    description="Fallback crew for open-ended conversation and chit-chat.",
    match_fn=_always,
)

# The *ordering* matters – first match wins.
_SPEC_REGISTRY: list[CrewSpec] = []


def register_spec(spec: CrewSpec) -> None:
    """Register a custom crew spec, avoiding duplicates."""
    if spec not in _SPEC_REGISTRY:
        _SPEC_REGISTRY.append(spec)


def default_specs() -> List[CrewSpec]:
    """
    Return the registry of specs, ensuring the default conversational crew is the fallback.
    """
    specs = [s for s in _SPEC_REGISTRY if s.name != "general_chat"]
    specs.append(_CONVERSATION_CREW)
    return specs 