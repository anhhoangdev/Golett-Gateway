"""
Domain-Specific Chatbot Framework for Golett

This module provides abstract base classes and patterns for creating
specialized chatbots for different domains (BI, customer support, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum

from crewai import Agent, Task, Crew

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.session.session_manager import SessionManager
from golett.memory.contextual.context_manager import ContextManager
from golett.knowledge.sources import GolettAdvancedTextFileKnowledgeSource, KnowledgeRetrievalStrategy
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationType(Enum):
    """Standard conversation types for domain chatbots"""
    DATA_ANALYSIS = "data_analysis"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"
    CONVERSATIONAL = "conversational"
    EXPLANATION = "explanation"
    GREETING = "greeting"
    HELP = "help"


class DomainChatbotBase(ABC):
    """
    Abstract base class for domain-specific chatbots.
    
    This class provides the common patterns and infrastructure needed
    for building specialized chatbots in different domains.
    """
    
    def __init__(
        self,
        domain_name: str,
        session_id: str = None,
        user_id: str = "default_user",
        postgres_connection: str = None,
        qdrant_url: str = "http://localhost:6333",
        language: str = "english",
        **domain_specific_config
    ):
        """
        Initialize the domain chatbot.
        
        Args:
            domain_name: Name of the domain (e.g., "business_intelligence", "customer_support")
            session_id: Session identifier
            user_id: User identifier
            postgres_connection: PostgreSQL connection string
            qdrant_url: Qdrant URL for vector storage
            language: Primary language for the chatbot
            **domain_specific_config: Domain-specific configuration
        """
        self.domain_name = domain_name
        self.user_id = user_id
        self.language = language
        self.domain_config = domain_specific_config
        
        # Initialize Golett core system
        self._initialize_golett_core(postgres_connection, qdrant_url)
        
        # Initialize session
        self._initialize_session(session_id)
        
        # Initialize domain-specific components
        self._initialize_domain_components()
        
        # Initialize agents and tasks
        self._initialize_agents()
        self._initialize_task_factory()
        
        logger.info(f"✅ {domain_name} chatbot initialized (session: {self.session_id})")
    
    def _initialize_golett_core(self, postgres_connection: str, qdrant_url: str):
        """Initialize Golett's core memory and context management system"""
        if not postgres_connection:
            postgres_connection = os.getenv('POSTGRES_CONNECTION')
        
        if not postgres_connection:
            raise ValueError(
                f"PostgreSQL connection required for {self.domain_name} chatbot. "
                "Set POSTGRES_CONNECTION environment variable or pass postgres_connection parameter."
            )
        
        # Initialize memory manager with domain-specific configuration
        self.memory_manager = MemoryManager(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            postgres_base_table=f"{self.domain_name}_chatbot_memories",
            qdrant_base_collection=f"{self.domain_name}_chatbot_vectors",
            enable_normalized_layers=True
        )
        
        # Initialize session and context managers
        self.session_manager = SessionManager(self.memory_manager)
        self.context_manager = ContextManager(self.memory_manager)
        
        logger.info("✅ Golett core system initialized")
    
    def _initialize_session(self, session_id: str = None):
        """Initialize or create session with proper metadata"""
        session_metadata = {
            "domain": self.domain_name,
            "language": self.language,
            "version": "domain_framework",
            **self.domain_config
        }
        
        if session_id:
            self.session_id = session_id
            session_info = self.session_manager.get_session_info(session_id)
            if not session_info:
                logger.info(f"Creating new session with ID: {session_id}")
                self.session_manager.create_session(
                    user_id=self.user_id,
                    session_type=f"{self.domain_name}_chatbot",
                    metadata=session_metadata
                )
        else:
            self.session_id = self.session_manager.create_session(
                user_id=self.user_id,
                session_type=f"{self.domain_name}_chatbot",
                preferences={
                    "language": self.language,
                    "domain": self.domain_name
                },
                metadata=session_metadata
            )
        
        logger.info(f"✅ Session initialized: {self.session_id}")
    
    @abstractmethod
    def _initialize_domain_components(self):
        """Initialize domain-specific components (schemas, APIs, etc.)"""
        pass
    
    @abstractmethod
    def _initialize_agents(self):
        """Initialize domain-specific agents"""
        pass
    
    @abstractmethod
    def _initialize_task_factory(self):
        """Initialize domain-specific task factory"""
        pass
    
    @abstractmethod
    def _classify_conversation_type(self, question: str) -> ConversationType:
        """Classify the type of conversation/question"""
        pass
    
    @abstractmethod
    def _get_domain_context(self, question: str, conversation_type: ConversationType) -> Dict[str, Any]:
        """Get domain-specific context for the question"""
        pass
    
    def ask(self, question: str) -> str:
        """
        Main entry point for asking questions.
        
        This method implements the common conversation flow pattern:
        1. Store user message
        2. Classify conversation type
        3. Get enhanced context
        4. Route to appropriate handler
        5. Store response and insights
        """
        try:
            logger.info(f"🤔 Processing {self.domain_name} question: {question}")
            
            # Store the user message
            self._store_user_message(question)
            
            # Classify conversation type
            conversation_type = self._classify_conversation_type(question)
            logger.info(f"🔍 Conversation type: {conversation_type.value}")
            
            # Get enhanced context
            enhanced_context = self._get_enhanced_context(question, conversation_type)
            
            # Route to appropriate handler
            answer = self._route_to_handler(question, conversation_type, enhanced_context)
            
            # Store response and insights
            self._store_response_and_insights(question, answer, conversation_type)
            
            return answer
            
        except Exception as e:
            error_msg = f"❌ Error processing {self.domain_name} question: {str(e)}"
            logger.error(error_msg)
            
            # Store error for learning
            self._store_error(question, error_msg)
            
            return error_msg
    
    def _get_enhanced_context(self, question: str, conversation_type: ConversationType) -> Dict[str, Any]:
        """
        Get enhanced context combining domain-specific and general context.
        
        This method provides a standard pattern for context retrieval that
        can be customized by domain implementations.
        """
        try:
            # Get domain-specific context
            domain_context = self._get_domain_context(question, conversation_type)
            
            # Get general conversation context
            general_context = self._get_general_context(question, conversation_type)
            
            # Combine contexts
            enhanced_context = {
                **domain_context,
                **general_context,
                "conversation_type": conversation_type.value,
                "domain": self.domain_name,
                "language": self.language
            }
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return {
                "conversation_context": [],
                "domain_context": {},
                "error": str(e)
            }
    
    def _get_general_context(self, question: str, conversation_type: ConversationType) -> Dict[str, Any]:
        """Get general context that applies to all domains"""
        try:
            # Get recent conversation
            recent_conversation = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=self._get_context_limit(conversation_type),
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            # Get semantic memories if needed
            semantic_memories = []
            if conversation_type in [ConversationType.DATA_ANALYSIS, ConversationType.EXPLANATION]:
                semantic_memories = self._semantic_memory_search(question, limit=3)
            
            # Get user preferences
            user_preferences = self._get_user_preferences()
            
            return {
                "conversation_context": recent_conversation,
                "semantic_memories": semantic_memories,
                "user_preferences": user_preferences
            }
            
        except Exception as e:
            logger.warning(f"Error getting general context: {e}")
            return {
                "conversation_context": [],
                "semantic_memories": [],
                "user_preferences": {}
            }
    
    def _get_context_limit(self, conversation_type: ConversationType) -> int:
        """Get context limit based on conversation type"""
        limits = {
            ConversationType.DATA_ANALYSIS: 5,
            ConversationType.FOLLOW_UP: 8,
            ConversationType.CLARIFICATION: 6,
            ConversationType.EXPLANATION: 6,
            ConversationType.CONVERSATIONAL: 3,
            ConversationType.GREETING: 2,
            ConversationType.HELP: 4
        }
        return limits.get(conversation_type, 5)
    
    def _semantic_memory_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search across memory layers"""
        try:
            results = self.memory_manager.search_across_all_layers(
                query=query,
                session_id=self.session_id,
                limit=limit,
                include_layer_weights=True
            )
            
            formatted_results = []
            for result in results:
                formatted_result = {
                    "content": result.get("data", ""),
                    "metadata": result.get("metadata", {}),
                    "similarity_score": result.get("score", 0.0),
                    "memory_layer": result.get("metadata", {}).get("searched_in_layer", "unknown"),
                    "timestamp": result.get("metadata", {}).get("timestamp", "")
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.warning(f"Error in semantic memory search: {e}")
            return []
    
    def _get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from session metadata"""
        try:
            session_info = self.session_manager.get_session_info(self.session_id)
            if session_info and "preferences" in session_info:
                return session_info["preferences"]
            return {}
        except Exception as e:
            logger.warning(f"Error getting user preferences: {e}")
            return {}
    
    @abstractmethod
    def _route_to_handler(self, question: str, conversation_type: ConversationType, enhanced_context: Dict[str, Any]) -> str:
        """Route to appropriate handler based on conversation type"""
        pass
    
    def _store_user_message(self, question: str):
        """Store user message in memory"""
        try:
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="user",
                content=question,
                metadata={
                    "language": self.language,
                    "domain": self.domain_name,
                    "timestamp": datetime.now().isoformat()
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
        except Exception as e:
            logger.warning(f"Error storing user message: {e}")
    
    def _store_response_and_insights(self, question: str, answer: str, conversation_type: ConversationType):
        """Store response and extract insights"""
        try:
            # Store assistant response
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="assistant",
                content=answer,
                metadata={
                    "language": self.language,
                    "domain": self.domain_name,
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "conversation_type": conversation_type.value
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Extract and store domain-specific insights
            self._extract_and_store_domain_insights(question, answer, conversation_type)
            
        except Exception as e:
            logger.warning(f"Error storing response and insights: {e}")
    
    @abstractmethod
    def _extract_and_store_domain_insights(self, question: str, answer: str, conversation_type: ConversationType):
        """Extract and store domain-specific insights"""
        pass
    
    def _store_error(self, question: str, error_msg: str):
        """Store error for learning"""
        try:
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="system",
                content=f"Error: {error_msg}",
                metadata={
                    "type": "error",
                    "question": question,
                    "domain": self.domain_name,
                    "timestamp": datetime.now().isoformat()
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
        except Exception as e:
            logger.warning(f"Error storing error message: {e}")
    
    # Utility methods for common chatbot operations
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            session_info = self.session_manager.get_session_info(self.session_id)
            layer_stats = self.memory_manager.get_layer_statistics()
            history = self.memory_manager.get_session_history(self.session_id, limit=1000)
            
            return {
                "session_info": session_info,
                "layer_statistics": layer_stats,
                "conversation_count": len(history),
                "session_id": self.session_id,
                "domain": self.domain_name,
                "language": self.language,
                "memory_backend": "Golett Memory System"
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history"""
        try:
            return self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=limit,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def clear_session_memory(self):
        """Clear current session memory"""
        try:
            self.session_manager.close_session(self.session_id)
            
            self.session_id = self.session_manager.create_session(
                user_id=self.user_id,
                session_type=f"{self.domain_name}_chatbot",
                preferences={
                    "language": self.language,
                    "domain": self.domain_name
                }
            )
            
            logger.info(f"🧹 Session memory cleared, new session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test domain-specific connections and components"""
        pass


class DomainAgentBase(ABC):
    """
    Abstract base class for domain-specific agents.
    
    This provides common patterns for creating specialized agents
    with proper Golett integration.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        session_id: str,
        context_manager: ContextManager = None,
        agent_name: str = None,
        domain: str = None
    ):
        self.memory_manager = memory_manager
        self.session_id = session_id
        self.context_manager = context_manager or ContextManager(memory_manager)
        self.agent_name = agent_name or self.__class__.__name__
        self.domain = domain or "general"
        
        # Create the agent
        self.agent = self._create_agent()
    
    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with domain-specific configuration"""
        pass
    
    def get_enhanced_context(self, question: str) -> Dict[str, Any]:
        """Get enhanced context for this agent's domain"""
        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "session_id": self.session_id
        }


class DomainTaskFactoryBase(ABC):
    """
    Abstract base class for domain-specific task factories.
    
    This provides common patterns for creating tasks with proper
    context and memory integration.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        context_manager: ContextManager,
        session_id: str,
        domain: str = None
    ):
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
        self.domain = domain or "general"
    
    @abstractmethod
    def create_task_for_type(
        self,
        conversation_type: ConversationType,
        question: str,
        agent: Agent,
        enhanced_context: Dict[str, Any]
    ) -> Task:
        """Create a task for the given conversation type"""
        pass
    
    def _create_base_task(
        self,
        description: str,
        agent: Agent,
        expected_output: str = "A complete and helpful response"
    ) -> Task:
        """Create a base task with common configuration"""
        return Task(
            description=description,
            agent=agent,
            expected_output=expected_output
        ) 