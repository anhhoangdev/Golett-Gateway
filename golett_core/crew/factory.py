from __future__ import annotations

"""Factory responsible for instantiating a concrete crew from a :class:`CrewSpec`.

This implementation now wires the `golett_core.crew.Orchestrator` (our
CrewAI wrapper) so that requests are executed by *real* agents rather
than the previous echo stub.  If you register additional specialised
`CrewSpec` objects you can extend :py:meth:`create_and_run` to branch on
`spec.requires_knowledge` or other metadata.
"""

from typing import List

from golett_core.crew.spec import CrewSpec
from golett_core.schemas.memory import ChatMessage
from golett_core.interfaces import MemoryInterface
from golett_core.crew.orchestrator import Orchestrator
from golett_core.crew.rag_orchestrator import RAGOrchestrator
from golett_core.interfaces import KnowledgeInterface
from golett_core.interfaces import CrewFactoryInterface

__all__ = [
    "CrewFactory",
]


class CrewFactory(CrewFactoryInterface):
    """Reference implementation of :class:`CrewFactoryInterface`.

    Parameters
    ----------
    memory_core:
        Shared `MemoryInterface` instance to persist agent messages and
        conversation history.
    knowledge_handler:
        Optional `KnowledgeInterface` used to fetch RAG context when the
        selected :class:`CrewSpec` requires it (e.g., *knowledge_rag*).
    """

    def __init__(self, memory_core: MemoryInterface, knowledge_handler: KnowledgeInterface | None = None) -> None:  # noqa: D401
        self._memory_core = memory_core
        self._knowledge = knowledge_handler

    # ------------------------------------------------------------------

    async def create_and_run(self, spec: CrewSpec, prompt: str, history: List[ChatMessage]) -> str:  # type: ignore[D401]
        """Materialise the crew defined by *spec* and run it.

        The orchestration is delegated to the selected orchestrator.
        """
        # ---- 1. Pick orchestrator based on the spec ------------------
        if spec.requires_knowledge:
            if not self._knowledge:
                raise ValueError(
                    "Knowledge handler is required for this crew spec but was not provided."
                )
            orchestrator = RAGOrchestrator(
                memory_core=self._memory_core,
                knowledge_handler=self._knowledge,
            )
        else:
            orchestrator = Orchestrator(memory_core=self._memory_core)

        # ---- 2. Delegate execution ------------------------------------
        result = await orchestrator.run(prompt)

        return result 