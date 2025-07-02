from __future__ import annotations
from typing import Any, Dict, List
from uuid import UUID

from crewai import Crew
from pydantic import ConfigDict

from golett_core.interfaces import MemoryInterface
from golett_core.schemas.memory import ChatMessage, ChatRole


class GolettCrew(Crew):
    """
    A custom Crew that integrates Golett's memory system.
    """
    
    golett_memory: MemoryInterface
    session_id: UUID

    # Pydantic v2 requires explicit permission to use non-pydantic types as
    # model fields.  Setting `arbitrary_types_allowed=True` prevents schema
    # generation errors for custom classes such as `GolettMemoryCore`.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self, 
        golett_memory: MemoryInterface, 
        session_id: UUID,
        **kwargs: Any
    ):
        # Forward mandatory fields to the underlying Pydantic model so that
        # validation does not fail (they are declared as model fields above).
        super().__init__(golett_memory=golett_memory, session_id=session_id, **kwargs)
        # Disable CrewAI's internal memory management
        self.memory = False 

    async def save_user_message(self, message: str):
        """Saves a user message to Golett's memory."""
        user_msg = ChatMessage(session_id=self.session_id, role=ChatRole.USER, content=message)
        await self.golett_memory.save_message(user_msg)

    async def save_assistant_message(self, message: str):
        """Saves an assistant message to Golett's memory."""
        # Ensure we always store plain text content in the memory layer.
        assistant_msg = ChatMessage(
            session_id=self.session_id,
            role=ChatRole.ASSISTANT,
            content=str(message),
        )
        await self.golett_memory.save_message(assistant_msg) 