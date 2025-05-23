from typing import Any, Dict, List, Optional, Union
import json
import uuid
from datetime import datetime, timedelta

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class SessionManager:
    """
    Manages session state, metadata, and lifecycle.
    
    This class provides methods for creating, retrieving, and managing
    session information beyond just messages, including session state,
    user preferences, and crew-related session data.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the session manager.
        
        Args:
            memory_manager: The memory manager instance to use for storage
        """
        self.memory_manager = memory_manager
        logger.info("Session Manager initialized")
    
    def create_session(
        self,
        user_id: str,
        session_type: str = "standard",
        preferences: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session with extended metadata.
        
        Args:
            user_id: Identifier for the user
            session_type: Type of session (e.g., "standard", "crew", "bi")
            preferences: Optional user preferences for this session
            metadata: Additional metadata (can include 'session_id' for custom ID)
            
        Returns:
            The session ID
        """
        # Extract custom session ID if provided in metadata
        custom_session_id = None
        if metadata and 'session_id' in metadata:
            custom_session_id = metadata['session_id']
            # Remove session_id from metadata to avoid duplication
            metadata = metadata.copy()
            del metadata['session_id']
        
        # Prepare metadata
        combined_metadata = {
            "user_id": user_id,
            "session_type": session_type,
            "preferences": preferences or {},
            "created_at": datetime.now().isoformat()
        }
        
        if metadata:
            combined_metadata.update(metadata)
        
        # Create session in memory manager with custom ID if provided
        session_id = self.memory_manager.create_session(
            metadata=combined_metadata,
            session_id=custom_session_id
        )
        
        # Store initial session state
        self.update_session_state(
            session_id=session_id,
            state={
                "status": "active",
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
                "crews": []
            }
        )
        
        logger.info(f"Created new session {session_id} for user {user_id}")
        return session_id
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive session information.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session metadata and state
        """
        # Get session metadata using layer-aware key format
        # Sessions are stored in short-term layer with format: st:{session_id}:session
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            session_key = f"st:{session_id}:session"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            # Backward compatibility
            session_key = f"session:{session_id}"
            postgres_storage = self.memory_manager.postgres
        
        session_data = postgres_storage.get(key=session_key)
        
        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return {}
        
        # Get session state using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            state_key = f"st:{session_id}:session_state"
        else:
            state_key = f"session_state:{session_id}"
            
        state_data = postgres_storage.get(key=state_key)
        
        # Combine data
        result = {
            "id": session_id,
            "metadata": session_data.get("metadata", {}),
            "data": session_data.get("data", {}),
            "state": state_data.get("data", {}) if state_data else {}
        }
        
        return result
    
    def update_session_state(
        self, 
        session_id: str, 
        state: Dict[str, Any]
    ) -> None:
        """
        Update the session state.
        
        Args:
            session_id: The session ID
            state: The new state data (will be merged with existing state)
        """
        # Get current state using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            state_key = f"st:{session_id}:session_state"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            state_key = f"session_state:{session_id}"
            postgres_storage = self.memory_manager.postgres
            
        current_state = postgres_storage.get(key=state_key)
        
        # Prepare new state (merge with existing)
        if current_state and "data" in current_state:
            new_state = current_state["data"].copy()
            new_state.update(state)
        else:
            new_state = state.copy()
        
        # Always update last_activity
        new_state["last_activity"] = datetime.now().isoformat()
        
        # Save updated state
        postgres_storage.save(
            key=state_key,
            data=new_state,
            metadata={
                "type": "session_state",
                "session_id": session_id
            }
        )
        
        logger.debug(f"Updated state for session {session_id}")
    
    def register_crew_with_session(
        self,
        session_id: str,
        crew_id: str,
        crew_name: str,
        agent_count: int,
        process_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a crew with a session.
        
        Args:
            session_id: The session ID
            crew_id: The crew ID
            crew_name: Human-readable name for the crew
            agent_count: Number of agents in the crew
            process_type: Process type (e.g., "sequential", "hierarchical")
            metadata: Additional metadata
        """
        # Get current state using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            state_key = f"st:{session_id}:session_state"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            state_key = f"session_state:{session_id}"
            postgres_storage = self.memory_manager.postgres
            
        current_state = postgres_storage.get(key=state_key)
        
        if not current_state:
            logger.warning(f"Session {session_id} not found")
            return
        
        # Get current crew list
        current_crews = current_state.get("data", {}).get("crews", [])
        
        # Prepare crew info
        crew_info = {
            "id": crew_id,
            "name": crew_name,
            "agent_count": agent_count,
            "process_type": process_type,
            "registered_at": datetime.now().isoformat(),
            "task_count": 0
        }
        
        if metadata:
            crew_info.update(metadata)
        
        # Add to list (replace if exists)
        new_crews = [c for c in current_crews if c.get("id") != crew_id]
        new_crews.append(crew_info)
        
        # Update state
        self.update_session_state(
            session_id=session_id,
            state={"crews": new_crews}
        )
        
        logger.info(f"Registered crew {crew_id} with session {session_id}")
    
    def update_crew_task_count(
        self,
        session_id: str,
        crew_id: str,
        increment: int = 1
    ) -> None:
        """
        Update the task count for a crew in a session.
        
        Args:
            session_id: The session ID
            crew_id: The crew ID
            increment: Amount to increment the task count by
        """
        # Get current state using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            state_key = f"st:{session_id}:session_state"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            state_key = f"session_state:{session_id}"
            postgres_storage = self.memory_manager.postgres
            
        current_state = postgres_storage.get(key=state_key)
        
        if not current_state or "data" not in current_state:
            logger.warning(f"Session {session_id} not found")
            return
        
        # Get current crew list
        current_crews = current_state["data"].get("crews", [])
        
        # Find and update the crew
        new_crews = []
        for crew in current_crews:
            if crew.get("id") == crew_id:
                updated_crew = crew.copy()
                updated_crew["task_count"] = crew.get("task_count", 0) + increment
                updated_crew["last_activity"] = datetime.now().isoformat()
                new_crews.append(updated_crew)
            else:
                new_crews.append(crew)
        
        # Update state
        if new_crews != current_crews:
            self.update_session_state(
                session_id=session_id,
                state={"crews": new_crews}
            )
    
    def get_active_sessions(
        self,
        user_id: Optional[str] = None,
        inactive_threshold_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get active sessions.
        
        Args:
            user_id: Optional user ID to filter by
            inactive_threshold_hours: Hours of inactivity before a session is considered inactive
            
        Returns:
            List of active session info
        """
        # Build query
        query = {"type": "session"}
        if user_id:
            query["user_id"] = user_id
        
        # Get all matching sessions using appropriate storage
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            postgres_storage = self.memory_manager.postgres
            
        sessions = postgres_storage.search(
            query=query,
            limit=100  # Reasonable limit
        )
        
        # Filter to active sessions
        active_sessions = []
        threshold_time = datetime.now() - timedelta(hours=inactive_threshold_hours)
        threshold_str = threshold_time.isoformat()
        
        for session in sessions:
            session_id = session.get("metadata", {}).get("session_id")
            if not session_id:
                continue
                
            # Get session state to check activity using layer-aware key format
            if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
                state_key = f"st:{session_id}:session_state"
            else:
                state_key = f"session_state:{session_id}"
                
            state = postgres_storage.get(key=state_key)
            
            if not state:
                continue
                
            last_activity = state.get("data", {}).get("last_activity", "")
            status = state.get("data", {}).get("status", "")
            
            # Check if active
            if (status == "active" and last_activity >= threshold_str):
                # Combine session and state info
                session_info = {
                    "id": session_id,
                    "metadata": session.get("metadata", {}),
                    "state": state.get("data", {})
                }
                active_sessions.append(session_info)
        
        return active_sessions
    
    def close_session(self, session_id: str) -> None:
        """
        Close a session.
        
        Args:
            session_id: The session ID
        """
        # Update session state
        self.update_session_state(
            session_id=session_id,
            state={
                "status": "closed",
                "closed_at": datetime.now().isoformat()
            }
        )
        
        # Update session data using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            session_key = f"st:{session_id}:session"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            session_key = f"session:{session_id}"
            postgres_storage = self.memory_manager.postgres
            
        postgres_storage.save(
            key=session_key,
            data={"status": "closed", "closed_at": datetime.now().isoformat()},
            metadata={
                "type": "session",
                "session_id": session_id,
                "status": "closed"
            }
        )
        
        logger.info(f"Closed session {session_id}")
    
    def store_session_preferences(
        self,
        session_id: str,
        preferences: Dict[str, Any]
    ) -> None:
        """
        Store user preferences for a session.
        
        Args:
            session_id: The session ID
            preferences: User preferences
        """
        # Get current session data using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            session_key = f"st:{session_id}:session"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            # Backward compatibility
            session_key = f"session:{session_id}"
            postgres_storage = self.memory_manager.postgres
        
        session_data = postgres_storage.get(key=session_key)
        
        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return
        
        # Get current metadata
        metadata = session_data.get("metadata", {}).copy()
        
        # Update preferences
        current_prefs = metadata.get("preferences", {})
        updated_prefs = current_prefs.copy()
        updated_prefs.update(preferences)
        
        metadata["preferences"] = updated_prefs
        
        # Save updated session metadata
        postgres_storage.save(
            key=session_key,
            data=session_data.get("data", {}),
            metadata=metadata
        )
        
        logger.debug(f"Updated preferences for session {session_id}")
        
    def get_session_preferences(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get user preferences for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            User preferences
        """
        # Get session data using layer-aware key format
        if hasattr(self.memory_manager, 'enable_normalized_layers') and self.memory_manager.enable_normalized_layers:
            session_key = f"st:{session_id}:session"
            postgres_storage = self.memory_manager.layer_storage[MemoryLayer.SHORT_TERM]["postgres"]
        else:
            # Backward compatibility
            session_key = f"session:{session_id}"
            postgres_storage = self.memory_manager.postgres
        
        session_data = postgres_storage.get(key=session_key)
        
        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return {}
        
        # Return preferences
        return session_data.get("metadata", {}).get("preferences", {}) 