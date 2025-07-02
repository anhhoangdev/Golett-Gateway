from __future__ import annotations

from typing import List
from uuid import UUID

from golett_core.interfaces import SessionManagerInterface, KnowledgeInterface, CrewFactoryInterface
from golett_core.schemas import ChatMessage
from golett_core.executor.master_agent import MasterAgent
from golett_core.schemas.memory import ChatRole

class CrewExecutor:
    """Orchestrates triage, memory retrieval, knowledge retrieval, and crew run."""

    def __init__(
        self,
        session_manager: SessionManagerInterface,
        knowledge_handler: KnowledgeInterface,
        master_agent: MasterAgent,
    ) -> None:  # noqa: D401
        self._sessions = session_manager
        self._knowledge = knowledge_handler
        self._master_agent = master_agent

    # ------------------------------------------------------------------

    async def run(self, session_id: UUID, user_message: str) -> str:  # noqa: D401
        """Main entry: returns assistant response text."""
        # 1. Persist user message
        user_msg = ChatMessage(session_id=session_id, role=ChatRole.USER, content=user_message)
        await self._sessions.add_message(session_id, user_msg)

        # 2. We *do not* perform intent classification here anymore – the
        #    responsibility has been delegated to the MasterAgent.
        #    The index is kept for potential analytics but not used.

        # -------------------------------
        # 3. Gather history (cached)
        # -------------------------------
        history = await self._sessions.get_history(session_id, limit=10)

        # 4. The MasterAgent will now take over routing + execution.
        assistant_response = await self._master_agent.run(user_message, history)

        # 5. Persist assistant message
        assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=assistant_response)
        await self._sessions.add_message(session_id, assistant_msg)

        return assistant_response


__all__ = [
    "CrewExecutor",
] 