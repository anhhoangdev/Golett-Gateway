from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from crewai import Crew, Agent, Task
from crewai.agent import Agent as CrewAgent

from golett.chat.session import ChatSession
from golett.chat.crew import GolettKnowledgeAdapter
from golett.memory.memory_manager import MemoryManager
from golett.memory.contextual.context_manager import ContextManager
from golett.memory.session.session_manager import SessionManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class CrewChatSession(ChatSession):
    """
    Enhanced chat session with support for CrewAI crews.
    
    This class extends the standard ChatSession with capabilities for
    creating and managing CrewAI crews, which can be used for complex
    problem-solving and knowledge-intensive tasks.
    """
    
    def __init__(
        self, 
        memory_manager: MemoryManager,
        knowledge_adapter: Optional[GolettKnowledgeAdapter] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """
        Initialize the crew-enabled chat session.
        
        Args:
            memory_manager: The memory manager instance
            knowledge_adapter: Optional adapter for CrewAI knowledge integration
            session_id: Optional session ID (will create a new one if not provided)
            metadata: Additional metadata for the session
            user_id: Optional user identifier
        """
        super().__init__(memory_manager, session_id, metadata)
        
        # Initialize additional managers
        self.context_manager = ContextManager(memory_manager)
        self.session_manager = SessionManager(memory_manager)
        
        self.knowledge_adapter = knowledge_adapter
        self.crews = {}
        
        # Track if the session has knowledge capabilities
        self.has_knowledge = knowledge_adapter is not None
        
        # Register with the session manager if user ID provided
        if not session_id and user_id:
            # This is a new session with a user ID
            session_type = "crew" if self.has_knowledge else "standard"
            preferences = metadata.get("preferences", {}) if metadata else {}
            
            # Register extended session information
            self.session_manager.store_session_preferences(
                session_id=self.session_id,
                preferences=preferences
            )
        
        logger.info(f"Crew-enabled chat session initialized: {self.session_id}")
    
    def create_crew(
        self, 
        crew_id: str, 
        agents: List[CrewAgent], 
        tasks: Optional[List[Task]] = None,
        process: str = "sequential",
        verbose: bool = True,
        crew_name: Optional[str] = None
    ) -> Crew:
        """
        Create a CrewAI crew for this session.
        
        Args:
            crew_id: Unique identifier for the crew
            agents: List of CrewAI agents to include in the crew
            tasks: Optional list of predefined tasks for the crew
            process: Crew process type (e.g., "sequential", "hierarchical")
            verbose: Whether the crew should provide verbose output
            crew_name: Optional human-readable name for the crew
            
        Returns:
            The created crew instance
        """
        crew = Crew(
            agents=agents,
            tasks=tasks or [],
            process=process,
            verbose=verbose
        )
        
        # Store the crew in the session
        self.crews[crew_id] = crew
        
        # Use a human-readable name if provided, or generate one
        display_name = crew_name or f"Crew {crew_id[:8]}"
        
        # Register with session manager
        self.session_manager.register_crew_with_session(
            session_id=self.session_id,
            crew_id=crew_id,
            crew_name=display_name,
            agent_count=len(agents),
            process_type=process,
            metadata={
                "agent_roles": [agent.role for agent in agents]
            }
        )
        
        # Store crew creation in context manager
        self.context_manager.store_crew_context(
            session_id=self.session_id,
            crew_id=crew_id,
            context_type="crew_creation",
            data={
                "crew_id": crew_id,
                "crew_name": display_name,
                "agent_count": len(agents),
                "agent_roles": [agent.role for agent in agents],
                "process": process
            }
        )
        
        logger.info(f"Created crew '{display_name}' ({crew_id}) with {len(agents)} agents")
        return crew
    
    def execute_crew_task(
        self, 
        crew_id: str, 
        task_description: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using a crew.
        
        Args:
            crew_id: The ID of the crew to use
            task_description: Description of the task to perform
            inputs: Optional additional inputs for the task
            
        Returns:
            The result of the crew execution
        """
        if crew_id not in self.crews:
            raise ValueError(f"Crew '{crew_id}' not found in this session")
        
        crew = self.crews[crew_id]
        
        # Create a task for the crew to execute
        from crewai import Task
        
        # Use the first agent in the crew as the task agent
        if not crew.agents:
            raise ValueError(f"Crew '{crew_id}' has no agents")
        
        task_agent = crew.agents[0]  # Use first agent for the task
        
        task = Task(
            description=task_description,
            agent=task_agent,
            expected_output="A complete response to the task"
        )
        
        # Create a new crew with the task
        from crewai import Crew
        task_crew = Crew(
            agents=crew.agents,
            tasks=[task],
            verbose=crew.verbose,
            process=crew.process
        )
        
        logger.info(f"Executing task with crew '{crew_id}': {task_description[:50]}...")
        
        # Update task count in session manager
        self.session_manager.update_crew_task_count(
            session_id=self.session_id,
            crew_id=crew_id,
            increment=1
        )
        
        # Store task in context manager
        task_id = self.context_manager.store_crew_context(
            session_id=self.session_id,
            crew_id=crew_id,
            context_type="task",
            data={
                "description": task_description,
                "inputs": inputs
            }
        )
        
        # Execute the crew task
        result = task_crew.kickoff(inputs=inputs)
        
        # Extract the result text and create a serializable result object
        result_text = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        # Safely extract usage metrics if available
        usage_info = {}
        if hasattr(result, 'token_usage') and result.token_usage:
            try:
                # Try to extract basic usage info safely
                usage_obj = result.token_usage
                if hasattr(usage_obj, 'total_tokens'):
                    usage_info['total_tokens'] = getattr(usage_obj, 'total_tokens', 0)
                if hasattr(usage_obj, 'prompt_tokens'):
                    usage_info['prompt_tokens'] = getattr(usage_obj, 'prompt_tokens', 0)
                if hasattr(usage_obj, 'completion_tokens'):
                    usage_info['completion_tokens'] = getattr(usage_obj, 'completion_tokens', 0)
                if hasattr(usage_obj, 'total_cost'):
                    usage_info['total_cost'] = getattr(usage_obj, 'total_cost', 0.0)
            except Exception:
                # If we can't extract usage info, just skip it
                usage_info = {"note": "Usage metrics not available"}
        
        # Create a serializable result dictionary
        serializable_result = {
            "result": result_text,
            "task_description": task_description,
            "crew_id": crew_id,
            "agent_count": len(crew.agents),
            "usage_metrics": usage_info,
            "execution_timestamp": datetime.now().isoformat()
        }
        
        # Add execution time if available
        if hasattr(result, 'execution_time'):
            try:
                exec_time = result.execution_time
                if isinstance(exec_time, (int, float)):
                    serializable_result["execution_time"] = exec_time
                else:
                    serializable_result["execution_time"] = str(exec_time)
            except Exception:
                pass
        
        # Store the result in context manager
        result_id = self.context_manager.store_crew_context(
            session_id=self.session_id,
            crew_id=crew_id,
            context_type="task_result",
            data=serializable_result,
            importance=0.8,  # Higher importance for crew results
            metadata={
                "task_id": task_id,
                "task_description": task_description
            }
        )
        
        logger.info(f"Stored crew result with ID: {result_id}")
        
        return {
            "crew_id": crew_id,
            "result": result_text,
            "result_id": result_id
        }
    
    def get_crew(self, crew_id: str) -> Optional[Crew]:
        """
        Get a crew by ID.
        
        Args:
            crew_id: The ID of the crew to retrieve
            
        Returns:
            The crew instance or None if not found
        """
        return self.crews.get(crew_id)
    
    def get_crew_results(
        self, 
        crew_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve previous crew results.
        
        Args:
            crew_id: Optional specific crew ID to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of crew results
        """
        return self.context_manager.retrieve_crew_context(
            session_id=self.session_id,
            crew_id=crew_id,
            context_type="task_result",
            limit=limit
        )
    
    def store_conversation_summary(
        self,
        summary: str,
        topics: List[str],
        start_message_index: int = 0,
        end_message_index: Optional[int] = None
    ) -> str:
        """
        Store a summary of the conversation.
        
        Args:
            summary: The conversation summary
            topics: List of topics covered in the summary
            start_message_index: Starting index in the message history
            end_message_index: Ending index in the message history (None for latest)
            
        Returns:
            The ID of the stored summary
        """
        # Get message history
        history = self.get_message_history()
        
        # Determine time boundaries
        if not history:
            return None
            
        end_index = end_message_index if end_message_index is not None else len(history) - 1
        
        if start_message_index < 0 or start_message_index >= len(history) or end_index >= len(history):
            raise ValueError("Invalid message index range")
            
        # Get timestamps
        start_time = history[start_message_index].get("metadata", {}).get("timestamp", "")
        end_time = history[end_index].get("metadata", {}).get("timestamp", "")
        
        # Store the summary
        return self.context_manager.store_conversation_summary(
            session_id=self.session_id,
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            topics=topics,
            metadata={
                "start_index": start_message_index,
                "end_index": end_index,
                "message_count": end_index - start_message_index + 1
            }
        )
        
    def close(self) -> None:
        """Close the session."""
        # Use session manager to close
        self.session_manager.close_session(self.session_id)
        self.active = False
        logger.info(f"Crew chat session closed: {self.session_id}") 