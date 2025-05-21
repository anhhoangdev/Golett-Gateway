import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from golett.memory.memory_manager import MemoryManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class ChatSession:
    """
    Manages a conversation session between a user and the agent system.
    
    This class handles message flow, maintains conversation state,
    and interfaces with the memory system.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a chat session.
        
        Args:
            memory_manager: The memory manager instance
            session_id: Optional session ID (will create a new one if not provided)
            metadata: Additional metadata for the session
        """
        self.memory_manager = memory_manager
        self.session_id = session_id or memory_manager.create_session(metadata)
        self.metadata = metadata or {}
        self.active = True
        
        logger.info(f"Chat session initialized: {self.session_id}")
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a user message to the session.
        
        Args:
            content: The message content
            metadata: Additional metadata for the message
            
        Returns:
            The message ID
        """
        return self.memory_manager.store_message(
            session_id=self.session_id,
            role="user",
            content=content,
            metadata=metadata
        )
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an assistant message to the session.
        
        Args:
            content: The message content
            metadata: Additional metadata for the message
            
        Returns:
            The message ID
        """
        return self.memory_manager.store_message(
            session_id=self.session_id,
            role="assistant",
            content=content,
            metadata=metadata
        )
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a system message to the session.
        
        Args:
            content: The message content
            metadata: Additional metadata for the message
            
        Returns:
            The message ID
        """
        return self.memory_manager.store_message(
            session_id=self.session_id,
            role="system",
            content=content,
            metadata=metadata
        )
    
    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the message history for this session.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in chronological order
        """
        return self.memory_manager.get_session_history(
            session_id=self.session_id,
            limit=limit
        )
    
    def search_messages(
        self, 
        query: str, 
        semantic: bool = True,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search through the session's message history.
        
        Args:
            query: The search query
            semantic: Whether to use semantic search
            limit: Maximum number of results to return
            
        Returns:
            List of matching messages
        """
        return self.memory_manager.search_message_history(
            query=query,
            session_id=self.session_id,
            semantic=semantic,
            limit=limit
        )
    
    def get_context_for_query(
        self, 
        query: str, 
        context_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context for a query.
        
        Args:
            query: The user query
            context_types: Optional list of context types to include
            limit: Maximum number of context items to return
            
        Returns:
            List of relevant context items
        """
        return self.memory_manager.retrieve_context(
            session_id=self.session_id,
            query=query,
            context_types=context_types,
            limit=limit
        )
    
    def store_bi_decision(
        self,
        should_use_data: bool,
        reasoning: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a decision about whether to use BI data for a response.
        
        Args:
            should_use_data: Whether BI data should be used
            reasoning: Reasoning behind the decision
            details: Additional details about the decision
            
        Returns:
            The decision ID
        """
        description = "Use BI data" if should_use_data else "Do not use BI data"
        
        metadata = details or {}
        metadata["should_use_data"] = should_use_data
        
        return self.memory_manager.store_decision(
            session_id=self.session_id,
            decision_type="use_bi_data",
            description=description,
            reasoning=reasoning,
            metadata=metadata
        )
    
    def store_response_mode_decision(
        self,
        response_mode: str,
        reasoning: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a decision about the response mode.
        
        Args:
            response_mode: The chosen response mode (e.g., "analytical", "conversational")
            reasoning: Reasoning behind the decision
            details: Additional details about the decision
            
        Returns:
            The decision ID
        """
        metadata = details or {}
        metadata["response_mode"] = response_mode
        
        return self.memory_manager.store_decision(
            session_id=self.session_id,
            decision_type="response_mode",
            description=f"Response mode: {response_mode}",
            reasoning=reasoning,
            metadata=metadata
        )
    
    def get_recent_decisions(self, decision_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent decisions for this session.
        
        Args:
            decision_type: Optional decision type to filter by
            limit: Maximum number of decisions to return
            
        Returns:
            List of recent decisions
        """
        return self.memory_manager.get_recent_decisions(
            session_id=self.session_id,
            decision_type=decision_type,
            limit=limit
        )
    
    def close(self) -> None:
        """Close the session."""
        self.active = False
        
        # Update session status in memory
        session_data = {
            "status": "closed",
            "closed_at": datetime.now().isoformat()
        }
        
        self.memory_manager.postgres.save(
            key=f"session:{self.session_id}",
            data=session_data,
            metadata={
                "type": "session",
                "session_id": self.session_id,
                "status": "closed"
            }
        )
        
        logger.info(f"Chat session closed: {self.session_id}")
        
    def is_active(self) -> bool:
        """Check if the session is active."""
        return self.active 