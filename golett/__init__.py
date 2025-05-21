"""
Golett - A modular, long-term conversational agent framework 
built on top of CrewAI with enhanced memory capabilities.

This package provides a system for managing persistent chat sessions
with agents capable of analyzing BI-related queries, deciding on
data utilization, and responding appropriately.
"""

__version__ = "0.1.0"

from golett.memory.memory_manager import MemoryManager
from golett.chat.session import ChatSession
from golett.chat.flow import ChatFlowManager
from golett.chat.crew import GolettKnowledgeAdapter
from golett.chat.crew_session import CrewChatSession
from golett.chat.crew_flow import CrewChatFlowManager

__all__ = [
    "MemoryManager",
    "ChatSession",
    "ChatFlowManager",
    "GolettKnowledgeAdapter",
    "CrewChatSession",
    "CrewChatFlowManager",
] 