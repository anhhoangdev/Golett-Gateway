#!/usr/bin/env python3
"""
Refactored Vietnamese Business Intelligence Chatbot with Selective Memory Layer Management

This refactored version uses Golett's latest capabilities with PROPER memory layer management:
- CrewChatSession and CrewChatFlowManager for crew-based conversation management
- EnhancedContextManager for sophisticated context retrieval
- GolettKnowledgeAdapter for knowledge management
- SELECTIVE MEMORY LAYER USAGE (key improvement):
  * IN-MEMORY: Always used for current conversation context
  * SHORT-TERM: Stores summaries, retrieved selectively for follow-ups and analysis
  * LONG-TERM: Stores insights, retrieved only for complex analysis
- Automatic summarization every 10 messages
- Clean, modern architecture using Golett's crew system
- Proper separation of agents and tasks into dedicated modules

KEY MEMORY IMPROVEMENTS:
- No longer retrieves from all layers for every query
- Creates summaries for short-term and insights for long-term storage
- Uses selective retrieval based on conversation type and strategy
- Implements proper memory layer separation as intended by Golett architecture
"""

import os
import sys
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, Process

# Golett core imports - updated to use crew system
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.session.session_manager import SessionManager
from golett.memory.contextual.context_manager import ContextManager
from golett.memory.contextual.enhanced_context_manager import EnhancedContextManager, ContextRetrievalStrategy
from golett.crew.crew_session import CrewChatSession
from golett.crew.crew_flow import CrewChatFlowManager
from golett.crew.crew import GolettKnowledgeAdapter
from golett.knowledge.sources import GolettAdvancedTextFileKnowledgeSource, KnowledgeRetrievalStrategy
from golett.utils.logger import get_logger

# Local imports - using proper agent and task modules
from chatbot_vietnamese.utils.dynamic_schema_mapper import DynamicCubeJSSchemaMapper
from chatbot_vietnamese.agents.vietnamese_bi_agents import (
    VietnameseDataAnalystAgent,
    VietnameseConversationClassifierAgent,
    VietnameseFollowUpAgent,
    VietnameseConversationalAgent,
    VietnameseExplanationAgent
)
from chatbot_vietnamese.agents.memory_decision_agent import VietnameseMemoryDecisionAgent
from chatbot_vietnamese.tasks.vietnamese_bi_tasks import VietnameseTaskFactory

logger = get_logger(__name__)


class RefactoredVietnameseCubeJSChatbot:
    """
    Refactored Vietnamese Business Intelligence Chatbot using Proper Agent and Task Classes
    
    This implementation now uses:
    - Proper agent classes from vietnamese_bi_agents.py module
    - Task factory from vietnamese_bi_tasks.py module
    - EnhancedContextManager for sophisticated context retrieval
    - GolettKnowledgeAdapter for knowledge management
    - Clean separation of concerns with dedicated agent and task modules
    
    Key improvements over the old version:
    - Uses proper agent classes instead of hardcoded agent definitions
    - Uses task factory for creating tasks with proper Golett integration
    - Enhanced context manager for better memory retrieval
    - Simplified architecture with better separation of concerns
    - Proper conversation flow based on question classification
    """
    
    def __init__(
        self, 
        session_id: str = None,
        user_id: str = "vietnamese_user",
        postgres_connection: str = None,
        qdrant_url: str = "http://localhost:6333",
        cubejs_api_url: str = "http://localhost:4000",
        cubejs_api_token: str = None,
    ):
        """
        Initialize Refactored Vietnamese CubeJS Chatbot with Crew System
        
        Args:
            session_id: Session identifier for memory management
            user_id: User identifier
            postgres_connection: PostgreSQL connection string for Golett memory
            qdrant_url: Qdrant URL for vector storage
            cubejs_api_url: CubeJS API URL
            cubejs_api_token: CubeJS API token
        """
        self.user_id = user_id
        self.cubejs_api_url = cubejs_api_url
        self.cubejs_api_token = cubejs_api_token
        
        # Get PostgreSQL connection from environment if not provided
        if not postgres_connection:
            postgres_connection = os.getenv('POSTGRES_CONNECTION')
        
        if not postgres_connection:
            raise ValueError(
                "PostgreSQL connection required for Vietnamese chatbot. "
                "Set POSTGRES_CONNECTION environment variable or pass postgres_connection parameter."
            )
        
        # Initialize Golett core system with crew support
        logger.info("🔧 Initializing Golett core system with crew support...")
        self._initialize_golett_core(postgres_connection, qdrant_url)
        
        # Initialize session
        self._initialize_session(session_id)
        
        # Initialize CubeJS components
        self.schema_mapper = DynamicCubeJSSchemaMapper()
        self.schema_mapper.refresh_schema()
        
        # Initialize knowledge sources
        self._initialize_knowledge_sources()
        
        # Initialize crew session and flow manager
        self._initialize_crew_system()
        
        logger.info(f"✅ Refactored Vietnamese CubeJS Chatbot with Crew System initialized (session: {self.session_id})")
    
    def _initialize_golett_core(self, postgres_connection: str, qdrant_url: str):
        """Initialize Golett's core memory and context management system"""
        
        # Initialize memory manager with proper configuration
        self.memory_manager = MemoryManager(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            postgres_base_table="vietnamese_chatbot_refactored_crew",
            qdrant_base_collection="vietnamese_chatbot_refactored_crew_vectors",
            enable_normalized_layers=True
        )
        
        # Initialize session manager
        self.session_manager = SessionManager(self.memory_manager)
        
        # Initialize enhanced context manager - key improvement!
        self.enhanced_context_manager = EnhancedContextManager(self.memory_manager)
        
        logger.info("✅ Golett core system with enhanced context manager initialized")
    
    def _initialize_session(self, session_id: str = None):
        """Initialize or create session with proper metadata"""
        
        if session_id:
            self.session_id = session_id
            # Verify session exists or create it
            session_info = self.session_manager.get_session_info(session_id)
            if not session_info:
                logger.info(f"Creating new session with ID: {session_id}")
                self.session_manager.create_session(
                    user_id=self.user_id,
                    session_type="vietnamese_bi_refactored_agent_classes",
                    metadata={
                        "session_id": session_id,
                        "version": "refactored_agent_classes",
                        "architecture": "agent_task_classes"
                    }
                )
        else:
            # Create new session
            self.session_id = self.session_manager.create_session(
                user_id=self.user_id,
                session_type="vietnamese_bi_refactored_agent_classes",
                preferences={
                    "language": "vietnamese", 
                    "domain": "business_intelligence",
                    "version": "refactored_agent_classes",
                    "architecture": "agent_task_classes"
                }
            )
        
        logger.info(f"✅ Session initialized: {self.session_id}")
    
    def _initialize_knowledge_sources(self):
        """Initialize CubeJS knowledge sources using Golett's knowledge system"""
        
        # Initialize knowledge adapter
        self.knowledge_adapter = GolettKnowledgeAdapter(
            memory_manager=self.memory_manager,
            session_id=self.session_id,
            enable_advanced_features=True,
            default_memory_layer=MemoryLayer.LONG_TERM,
            cross_session_access=True,
            max_knowledge_age_days=30
        )
        
        try:
            # Get the knowledge directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            knowledge_dir = os.path.join(project_root, "knowledge", "cubejs")
            
            # Initialize REST API knowledge source
            rest_api_path = os.path.join(knowledge_dir, "rest_api.md")
            if os.path.exists(rest_api_path):
                rest_api_source = self.knowledge_adapter.add_advanced_file_source(
                    file_path=rest_api_path,
                    collection_name="cubejs_rest_api_refactored_agent_classes",
                    memory_layer=MemoryLayer.LONG_TERM,
                    tags=["cubejs", "rest_api", "query_format", "vietnamese_refactored_agent_classes"],
                    importance=0.9,
                    chunk_size=800,
                    overlap_size=100
                )
                logger.info(f"✅ Loaded CubeJS REST API knowledge")
            
            # Initialize schemas knowledge source
            schemas_path = os.path.join(knowledge_dir, "schemas.md")
            if os.path.exists(schemas_path):
                schemas_source = self.knowledge_adapter.add_advanced_file_source(
                    file_path=schemas_path,
                    collection_name="cubejs_schemas_refactored_agent_classes",
                    memory_layer=MemoryLayer.LONG_TERM,
                    tags=["cubejs", "schemas", "data_model", "vietnamese_refactored_agent_classes"],
                    importance=0.9,
                    chunk_size=800,
                    overlap_size=100
                )
                logger.info(f"✅ Loaded CubeJS schemas knowledge")
            
            # Add memory-based knowledge source for conversation history
            memory_source = self.knowledge_adapter.add_advanced_memory_source(
                collection_names=["cubejs_rest_api_refactored_agent_classes", "cubejs_schemas_refactored_agent_classes"],
                memory_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
                context_types=["conversation", "insight", "data_analysis"],
                tags=["vietnamese_refactored_agent_classes", "cubejs"],
                importance_threshold=0.3,
                cross_session=True,
                max_age_days=30
            )
            logger.info(f"✅ Added memory-based knowledge source")
            
        except Exception as e:
            logger.warning(f"Error initializing knowledge sources: {e}")
    
    def _initialize_crew_system(self):
        """Initialize crew session and flow manager using proper agent and task classes"""
        
        # Create crew session
        self.crew_session = CrewChatSession(
            session_id=self.session_id,
            memory_manager=self.memory_manager,
            knowledge_adapter=self.knowledge_adapter
        )
        
        # Initialize agent classes with proper Golett integration
        self._initialize_agent_classes()
        
        # Initialize task factory
        self._initialize_task_factory()
        
        # Create specialized Vietnamese BI crews using agent classes
        self._create_vietnamese_crews_from_classes()
        
        # Create crew flow manager
        self.flow_manager = CrewChatFlowManager(
            session=self.crew_session,
            use_crew_for_complex=True,
            auto_summarize=True,
            messages_per_summary=8
        )
        
        logger.info("✅ Crew system initialized with Vietnamese BI agent classes")
    
    def _initialize_agent_classes(self):
        """Initialize Vietnamese BI agent classes with proper Golett integration"""
        
        # Get context for agents
        schema_context = self._generate_schema_context()
        knowledge_context = self._get_cubejs_context("CubeJS knowledge")
        
        # Initialize context manager for agents
        context_manager = ContextManager(self.memory_manager)
        
        # 1. Data Analyst Agent
        self.data_analyst_agent_class = VietnameseDataAnalystAgent(
            memory_manager=self.memory_manager,
            context_manager=context_manager,
            session_id=self.session_id,
            cubejs_api_url=self.cubejs_api_url,
            cubejs_api_token=self.cubejs_api_token,
            schema_context=schema_context,
            knowledge_context=knowledge_context
        )
        
        # 2. Conversation Classifier Agent
        self.classifier_agent_class = VietnameseConversationClassifierAgent(
            memory_manager=self.memory_manager,
            session_id=self.session_id
        )
        
        # 3. Follow-up Agent
        self.follow_up_agent_class = VietnameseFollowUpAgent(
            memory_manager=self.memory_manager,
            context_manager=context_manager,
            session_id=self.session_id
        )
        
        # 4. Conversational Agent
        self.conversational_agent_class = VietnameseConversationalAgent(
            memory_manager=self.memory_manager,
            session_id=self.session_id
        )
        
        # 5. Explanation Agent
        self.explanation_agent_class = VietnameseExplanationAgent(
            memory_manager=self.memory_manager,
            context_manager=context_manager,
            session_id=self.session_id
        )
        
        # 6. Memory Decision Agent (NEW - for intelligent memory layer decisions)
        self.memory_decision_agent = VietnameseMemoryDecisionAgent(
            memory_manager=self.memory_manager,
            context_manager=context_manager,
            session_id=self.session_id
        )
        
        logger.info("✅ Vietnamese BI agent classes initialized")
    
    def _initialize_task_factory(self):
        """Initialize task factory with Golett integration"""
        
        from golett.memory.contextual.context_manager import ContextManager
        context_manager = ContextManager(self.memory_manager)
        
        self.task_factory = VietnameseTaskFactory(
            memory_manager=self.memory_manager,
            context_manager=context_manager,
            session_id=self.session_id
        )
        
        logger.info("✅ Vietnamese task factory initialized")
    
    def _create_vietnamese_crews_from_classes(self):
        """Create specialized crews using proper agent classes"""
        
        # 1. Vietnamese Data Analysis Crew
        self.crew_session.create_crew(
            crew_id="vietnamese_data_analysis",
            crew_name="Vietnamese Data Analysis Team",
            agents=[
                self.data_analyst_agent_class.agent,
                # Could add query specialist here if needed
            ],
            process="sequential"
        )
        
        # 2. Vietnamese Conversation Management Crew
        self.crew_session.create_crew(
            crew_id="vietnamese_conversation",
            crew_name="Vietnamese Conversation Team",
            agents=[
                self.classifier_agent_class.agent,
                self.conversational_agent_class.agent,
                self.follow_up_agent_class.agent
            ],
            process="sequential"
        )
        
        # 3. Vietnamese Knowledge and Explanation Crew
        self.crew_session.create_crew(
            crew_id="vietnamese_knowledge",
            crew_name="Vietnamese Knowledge Team",
            agents=[
                self.explanation_agent_class.agent
            ],
            process="sequential"
        )
        
        logger.info("✅ Created specialized Vietnamese BI crews from agent classes")
    
    def _get_llm_config(self):
        """Get LLM configuration for agents"""
        # This would return the appropriate LLM configuration
        # For now, return None to use default
        return None

    def ask(self, question: str) -> str:
        """
        Ask a question using the proper agent classes and task factory
        
        Args:
            question: Vietnamese business question
            
        Returns:
            Answer with proper agent-based processing and enhanced Golett context
        """
        try:
            print(f"🤔 Processing question with agent classes and task factory: {question}")
            
            # Get enhanced context using the enhanced context manager
            enhanced_context = self._get_enhanced_context(question)
            
            # Step 1: Classify the conversation type using the classifier agent
            conversation_type = self._classify_question_with_agent(question)
            print(f"📋 Conversation type classified as: {conversation_type}")
            
            # Step 2: Process based on conversation type using appropriate agents and tasks
            response = self._process_by_conversation_type(question, conversation_type, enhanced_context)
            
            # Store the conversation with enhanced metadata
            self._store_conversation_with_metadata(question, response, enhanced_context)
            
            logger.info("✅ Question processed successfully with agent classes")
            return response
            
        except Exception as e:
            error_msg = f"❌ Lỗi khi xử lý câu hỏi: {str(e)}"
            print(error_msg)
            
            # Store error in memory for learning
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="system",
                content=f"Error: {error_msg}",
                metadata={
                    "type": "error",
                    "question": question,
                    "timestamp": datetime.now().isoformat(),
                    "version": "refactored_crew_agent_classes"
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            return error_msg
    
    def _classify_question_with_agent(self, question: str) -> str:
        """Classify question using the conversation classifier agent"""
        try:
            # Create classification task using task factory
            classification_task = self.task_factory.create_classification_task(
                question=question,
                agent=self.classifier_agent_class.agent
            )
            
            # Execute the classification task
            from crewai import Crew
            classification_crew = Crew(
                agents=[self.classifier_agent_class.agent],
                tasks=[classification_task],
                verbose=False
            )
            
            result = classification_crew.kickoff()
            classification = str(result).strip().lower()
            
            # Validate classification result
            valid_types = ["data_analysis", "follow_up_data_analysis", "follow_up", "conversational", "clarification"]
            if classification in valid_types:
                return classification
            else:
                # Fallback classification
                return self._classify_conversation_type(question)
                
        except Exception as e:
            logger.warning(f"Error in agent classification: {e}")
            # Fallback to rule-based classification
            return self._classify_conversation_type(question)
    
    def _process_by_conversation_type(self, question: str, conversation_type: str, enhanced_context: Dict[str, Any]) -> str:
        """Process question based on conversation type using appropriate agents and tasks"""
        
        try:
            if conversation_type == "data_analysis":
                return self._process_data_analysis(question, enhanced_context)
            
            elif conversation_type == "follow_up_data_analysis":
                return self._process_follow_up_data_analysis(question, enhanced_context)
            
            elif conversation_type == "follow_up":
                return self._process_follow_up(question, enhanced_context)
            
            elif conversation_type == "clarification":
                return self._process_explanation(question, enhanced_context)
            
            else:  # conversational
                return self._process_conversational(question, enhanced_context)
                
        except Exception as e:
            logger.error(f"Error processing conversation type {conversation_type}: {e}")
            # Fallback to conversational processing
            return self._process_conversational(question, enhanced_context)
    
    def _process_data_analysis(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Process data analysis questions using the data analyst agent"""
        try:
            print("📊 Processing as data analysis question...")
            
            # Create data analysis task using task factory
            data_analysis_task = self.task_factory.create_data_analysis_task(
                question=question,
                agent=self.data_analyst_agent_class.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute the data analysis task
            from crewai import Crew
            data_analysis_crew = Crew(
                agents=[self.data_analyst_agent_class.agent],
                tasks=[data_analysis_task],
                verbose=True
            )
            
            result = data_analysis_crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in data analysis processing: {e}")
            return f"❌ Lỗi khi phân tích dữ liệu: {str(e)}"
    
    def _process_follow_up_data_analysis(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Process follow-up data analysis questions using the data analyst agent"""
        try:
            print("📊 Processing as follow-up data analysis question...")
            
            # Create follow-up data analysis task using task factory
            follow_up_data_analysis_task = self.task_factory.create_follow_up_data_analysis_task(
                question=question,
                agent=self.data_analyst_agent_class.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute the follow-up data analysis task
            from crewai import Crew
            follow_up_data_analysis_crew = Crew(
                agents=[self.data_analyst_agent_class.agent],
                tasks=[follow_up_data_analysis_task],
                verbose=True
            )
            
            result = follow_up_data_analysis_crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in follow-up data analysis processing: {e}")
            return f"❌ Lỗi khi xử lý câu hỏi tiếp theo: {str(e)}"
    
    def _process_follow_up(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Process follow-up questions using the follow-up agent"""
        try:
            print("🔄 Processing as follow-up question...")
            
            # Create follow-up task using task factory
            follow_up_task = self.task_factory.create_follow_up_task(
                question=question,
                agent=self.follow_up_agent_class.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute the follow-up task
            from crewai import Crew
            follow_up_crew = Crew(
                agents=[self.follow_up_agent_class.agent],
                tasks=[follow_up_task],
                verbose=True
            )
            
            result = follow_up_crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in follow-up processing: {e}")
            return f"❌ Lỗi khi xử lý câu hỏi tiếp theo: {str(e)}"
    
    def _process_explanation(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Process explanation questions using the explanation agent"""
        try:
            print("💡 Processing as explanation question...")
            
            # Create explanation task using task factory
            explanation_task = self.task_factory.create_explanation_task(
                question=question,
                agent=self.explanation_agent_class.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute the explanation task
            from crewai import Crew
            explanation_crew = Crew(
                agents=[self.explanation_agent_class.agent],
                tasks=[explanation_task],
                verbose=True
            )
            
            result = explanation_crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in explanation processing: {e}")
            return f"❌ Lỗi khi giải thích: {str(e)}"
    
    def _process_conversational(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Process conversational questions using the conversational agent"""
        try:
            print("💬 Processing as conversational question...")
            
            # Get conversation context
            conversation_context = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=5,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            # Create conversational task using task factory
            conversational_task = self.task_factory.create_conversational_task(
                question=question,
                agent=self.conversational_agent_class.agent,
                conversation_context=conversation_context,
                enhanced_context=enhanced_context
            )
            
            # Execute the conversational task
            from crewai import Crew
            conversational_crew = Crew(
                agents=[self.conversational_agent_class.agent],
                tasks=[conversational_task],
                verbose=True
            )
            
            result = conversational_crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in conversational processing: {e}")
            return f"❌ Lỗi khi xử lý hội thoại: {str(e)}"
    
    def _get_enhanced_context(self, question: str) -> Dict[str, Any]:
        """Get enhanced context using proper memory layer strategy with selective retrieval"""
        
        try:
            # Determine the appropriate context retrieval strategy
            strategy = self._determine_context_strategy(question)
            conversation_type = self._classify_conversation_type(question)
            
            # ALWAYS get in-memory context (current conversation)
            in_memory_context = self._get_in_memory_context()
            
            # Selectively get short-term and long-term context based on need
            short_term_context = []
            long_term_context = []
            
            # Only retrieve from short-term/long-term for specific conversation types
            if self._should_use_short_term_memory(conversation_type, strategy):
                short_term_context = self._get_short_term_summaries(question)
            
            if self._should_use_long_term_memory(conversation_type, strategy):
                long_term_context = self._get_long_term_insights(question)
            
            # Get knowledge context (always available)
            knowledge_context = self._get_cubejs_context(question)
            
            return {
                "in_memory_context": in_memory_context,
                "short_term_summaries": short_term_context,
                "long_term_insights": long_term_context,
                "knowledge_context": knowledge_context,
                "context_type": "selective_layered",
                "retrieval_metadata": {
                    "strategy": strategy.value if hasattr(strategy, 'value') else str(strategy),
                    "conversation_type": conversation_type,
                    "used_short_term": len(short_term_context) > 0,
                    "used_long_term": len(long_term_context) > 0,
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return self._get_minimal_context(question)
    
    def _get_in_memory_context(self) -> List[Dict[str, Any]]:
        """Get current conversation context from in-memory layer only"""
        try:
            # Always get recent conversation from in-memory layer
            return self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=8,  # Recent conversation messages
                include_layers=[MemoryLayer.IN_SESSION]  # Only current session
            )
        except Exception as e:
            logger.warning(f"Error getting in-memory context: {e}")
            return []
    
    def _should_use_short_term_memory(self, conversation_type: str, strategy: str) -> bool:
        """Determine if short-term memory should be used based on conversation type"""
        
        # Follow-up questions should NOT use short-term memory - only in-memory
        if conversation_type == "follow_up":
            return False
        
        # Use short-term memory for data analysis and explanations
        short_term_types = [
            "data_analysis", 
            "follow_up_data_analysis",  # New type should use short-term memory
            "explanation",
            "clarification"
        ]
        
        # Use short-term for comprehensive and focused strategies
        short_term_strategies = [
            "comprehensive",
            "focused"
        ]
        
        return (conversation_type in short_term_types or 
                strategy in short_term_strategies)
    
    def _should_use_long_term_memory(self, conversation_type: str, strategy: str) -> bool:
        """Determine if long-term memory should be used based on conversation type"""
        
        # Follow-up questions should NOT use long-term memory - only in-memory
        if conversation_type == "follow_up":
            return False
        
        # Use long-term memory for complex analysis and knowledge questions
        long_term_types = [
            "data_analysis",
            "follow_up_data_analysis",  # New type should use long-term memory
            "explanation"
        ]
        
        # Use long-term for comprehensive strategy only
        long_term_strategies = [
            "comprehensive"
        ]
        
        return (conversation_type in long_term_types and 
                strategy in long_term_strategies)
    
    def _get_short_term_summaries(self, question: str) -> List[Dict[str, Any]]:
        """Get relevant summaries from short-term memory using enhanced semantic search"""
        try:
            # ENHANCED: Use semantic search across short-term memory with similarity scoring
            semantic_results = self.memory_manager.search_across_all_layers(
                query=question,
                session_id=self.session_id,
                limit=10,  # Get more results for filtering
                include_layer_weights=True
            )
            
            # Filter for SHORT_TERM layer only and apply similarity threshold
            short_term_results = []
            similarity_threshold = 0.3  # Minimum similarity for relevance
            
            for result in semantic_results:
                metadata = result.get("metadata", {})
                searched_layer = metadata.get("searched_in_layer", "")
                similarity_score = result.get("score", 0.0)
                weighted_score = result.get("weighted_score", similarity_score)
                
                # Only include SHORT_TERM results above similarity threshold
                if (searched_layer == MemoryLayer.SHORT_TERM.value and 
                    similarity_score >= similarity_threshold):
                    
                    # Enhanced context type filtering
                    context_type = metadata.get("context_type", "unknown")
                    relevant_context_types = [
                        "conversation_summary", "session_insight", "bi_analysis", 
                        "bi_data", "analysis_result", "user_preference", 
                        "business_insight", "data_pattern", "query_result"
                    ]
                    
                    if context_type in relevant_context_types:
                        short_term_results.append(result)
            
            # Sort by weighted similarity score (highest first)
            short_term_results.sort(key=lambda x: x.get("weighted_score", 0.0), reverse=True)
            
            # Take top 5 most relevant results
            top_results = short_term_results[:5]
            
            # Format summaries for agent consumption with enhanced metadata
            formatted_summaries = []
            for result in top_results:
                metadata = result.get("metadata", {})
                
                formatted_summary = {
                    "type": "short_term_summary",
                    "content": result.get("data", ""),
                    "summary_type": metadata.get("context_type", "unknown"),
                    "timestamp": metadata.get("timestamp", ""),
                    "importance": metadata.get("importance", 0.0),
                    "topics": metadata.get("topics", []),
                    "similarity_score": result.get("score", 0.0),
                    "weighted_score": result.get("weighted_score", result.get("score", 0.0)),
                    "layer_weight": metadata.get("layer_weight_applied", 0.0),
                    "search_method": "semantic_enhanced",
                    "relevance_reason": self._determine_relevance_reason(question, result.get("data", ""))
                }
                formatted_summaries.append(formatted_summary)
            
            logger.debug(f"Retrieved {len(formatted_summaries)} short-term summaries using enhanced semantic search")
            return formatted_summaries
            
        except Exception as e:
            logger.warning(f"Enhanced semantic search failed, falling back to basic retrieval: {e}")
            
            # FALLBACK: Use basic context retrieval if enhanced search fails
            try:
                summaries = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query=question,
                    context_types=["conversation_summary", "session_insight", "bi_analysis"],
                    limit=3,
                    include_layers=[MemoryLayer.SHORT_TERM],
                    cross_session=False
                )
                
                # Format with basic metadata
                formatted_summaries = []
                for summary in summaries:
                    formatted_summary = {
                        "type": "short_term_summary",
                        "content": summary.get("data", ""),
                        "summary_type": summary.get("metadata", {}).get("context_type", "unknown"),
                        "timestamp": summary.get("metadata", {}).get("timestamp", ""),
                        "importance": summary.get("metadata", {}).get("importance", 0.0),
                        "topics": summary.get("metadata", {}).get("topics", []),
                        "similarity_score": 0.5,  # Default score for fallback
                        "search_method": "basic_fallback"
                    }
                    formatted_summaries.append(formatted_summary)
                
                logger.debug(f"Retrieved {len(formatted_summaries)} short-term summaries using fallback method")
                return formatted_summaries
                
            except Exception as fallback_error:
                logger.error(f"Both enhanced and fallback short-term retrieval failed: {fallback_error}")
                return []
    
    def _get_long_term_insights(self, question: str) -> List[Dict[str, Any]]:
        """Get relevant insights from long-term memory using enhanced semantic search with cross-session capabilities"""
        try:
            # ENHANCED: Use semantic search across long-term memory with cross-session capabilities
            semantic_results = self.memory_manager.search_across_all_layers(
                query=question,
                session_id=None,  # Allow cross-session for long-term insights
                limit=15,  # Get more results for filtering
                include_layer_weights=True
            )
            
            # Filter for LONG_TERM layer only and apply similarity threshold
            long_term_results = []
            similarity_threshold = 0.4  # Higher threshold for long-term (more selective)
            
            for result in semantic_results:
                metadata = result.get("metadata", {})
                searched_layer = metadata.get("searched_in_layer", "")
                similarity_score = result.get("score", 0.0)
                weighted_score = result.get("weighted_score", similarity_score)
                
                # Only include LONG_TERM results above similarity threshold
                if (searched_layer == MemoryLayer.LONG_TERM.value and 
                    similarity_score >= similarity_threshold):
                    
                    # Enhanced context type filtering for long-term insights
                    context_type = metadata.get("context_type", "unknown")
                    relevant_context_types = [
                        "insight", "important_decision", "knowledge", "bi_pattern",
                        "business_insight", "strategic_insight", "data_pattern",
                        "user_behavior", "performance_metric", "trend_analysis",
                        "cross_session_insight", "historical_pattern"
                    ]
                    
                    if context_type in relevant_context_types:
                        long_term_results.append(result)
            
            # Sort by weighted similarity score (highest first)
            long_term_results.sort(key=lambda x: x.get("weighted_score", 0.0), reverse=True)
            
            # Take top 3 most relevant results (more selective for long-term)
            top_results = long_term_results[:3]
            
            # Format insights for agent consumption with enhanced metadata
            formatted_insights = []
            for result in top_results:
                metadata = result.get("metadata", {})
                result_session_id = metadata.get("session_id", "unknown")
                is_cross_session = result_session_id != self.session_id
                
                formatted_insight = {
                    "type": "long_term_insight",
                    "content": result.get("data", ""),
                    "insight_type": metadata.get("context_type", "unknown"),
                    "timestamp": metadata.get("timestamp", ""),
                    "importance": metadata.get("importance", 0.0),
                    "source_session": result_session_id,
                    "cross_session": is_cross_session,
                    "similarity_score": result.get("score", 0.0),
                    "weighted_score": result.get("weighted_score", result.get("score", 0.0)),
                    "layer_weight": metadata.get("layer_weight_applied", 0.0),
                    "search_method": "semantic_enhanced_cross_session",
                    "relevance_reason": self._determine_relevance_reason(question, result.get("data", "")),
                    "domain": metadata.get("domain", "unknown"),
                    "tags": metadata.get("tags", [])
                }
                formatted_insights.append(formatted_insight)
            
            logger.debug(f"Retrieved {len(formatted_insights)} long-term insights using enhanced semantic search "
                        f"({sum(1 for i in formatted_insights if i['cross_session'])} cross-session)")
            return formatted_insights
            
        except Exception as e:
            logger.warning(f"Enhanced semantic search for long-term failed, falling back to basic retrieval: {e}")
            
            # FALLBACK: Use basic context retrieval if enhanced search fails
            try:
                insights = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query=question,
                    context_types=["insight", "important_decision", "knowledge", "bi_pattern"],
                    limit=2,
                    include_layers=[MemoryLayer.LONG_TERM],
                    cross_session=True
                )
                
                # Format with basic metadata
                formatted_insights = []
                for insight in insights:
                    metadata = insight.get("metadata", {})
                    result_session_id = metadata.get("session_id", "unknown")
                    
                    formatted_insight = {
                        "type": "long_term_insight",
                        "content": insight.get("data", ""),
                        "insight_type": metadata.get("context_type", "unknown"),
                        "timestamp": metadata.get("timestamp", ""),
                        "importance": metadata.get("importance", 0.0),
                        "source_session": result_session_id,
                        "cross_session": result_session_id != self.session_id,
                        "similarity_score": 0.6,  # Default score for fallback
                        "search_method": "basic_fallback"
                    }
                    formatted_insights.append(formatted_insight)
                
                logger.debug(f"Retrieved {len(formatted_insights)} long-term insights using fallback method")
                return formatted_insights
                
            except Exception as fallback_error:
                logger.error(f"Both enhanced and fallback long-term retrieval failed: {fallback_error}")
                return []
    
    def _get_minimal_context(self, question: str) -> Dict[str, Any]:
        """Get minimal context when all else fails - only in-memory"""
        try:
            # Just get recent conversation history from in-memory
            in_memory_context = []
            try:
                in_memory_context = self.memory_manager.get_session_history(
                    session_id=self.session_id,
                    limit=3,
                    include_layers=[MemoryLayer.IN_SESSION]
                )
            except Exception as e:
                logger.warning(f"Error getting minimal in-memory context: {e}")
            
            return {
                "in_memory_context": in_memory_context,
                "short_term_summaries": [],
                "long_term_insights": [],
                "knowledge_context": "",
                "context_type": "minimal",
                "retrieval_metadata": {
                    "strategy": "minimal",
                    "conversation_type": self._classify_conversation_type(question),
                    "used_short_term": False,
                    "used_long_term": False,
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "minimal_fallback": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in minimal context retrieval: {e}")
            return {
                "in_memory_context": [],
                "short_term_summaries": [],
                "long_term_insights": [],
                "knowledge_context": "",
                "context_type": "error",
                "error": str(e),
                "retrieval_metadata": {
                    "strategy": "error",
                    "conversation_type": "unknown",
                    "used_short_term": False,
                    "used_long_term": False,
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "error": str(e)
                }
            }
    
    def _determine_context_strategy(self, question: str) -> ContextRetrievalStrategy:
        """Determine the appropriate context retrieval strategy based on the question"""
        
        question_lower = question.lower()
        
        # Data analysis questions need comprehensive context
        data_analysis_patterns = [
            "phân tích", "báo cáo", "thống kê", "doanh thu", "lợi nhuận", "bao nhiêu",
            "số lượng", "tăng trưởng", "giảm", "so sánh", "xu hướng"
        ]
        
        if any(pattern in question_lower for pattern in data_analysis_patterns):
            return ContextRetrievalStrategy.COMPREHENSIVE
        
        # Follow-up questions need contextual strategy (improved patterns)
        follow_up_patterns = [
            "tiếp tục", "thêm", "chi tiết", "cụ thể", "rõ ràng", "đầy đủ",
            "số liệu", "con số", "dữ liệu", "thông tin", "giải thích thêm",
            "nói thêm", "cho biết thêm", "bổ sung", "mở rộng", "phân tích thêm",
            "đừng chỉ", "không chỉ", "nhiều hơn", "sâu hơn", "rộng hơn",
            "cần thêm", "muốn thêm", "yêu cầu thêm", "làm rõ", "giải thích rõ",
            "giải thích", "tại sao", "vì sao"
        ]
        
        if any(pattern in question_lower for pattern in follow_up_patterns):
            return ContextRetrievalStrategy.CONTEXTUAL
        
        # Greetings and casual conversation
        greeting_patterns = [
            "xin chào", "chào", "cảm ơn", "tạm biệt", "hello", "hi", "bye"
        ]
        
        if any(pattern in question_lower for pattern in greeting_patterns):
            return ContextRetrievalStrategy.CONVERSATIONAL
        
        # Default to focused strategy
        return ContextRetrievalStrategy.FOCUSED
    
    def _classify_conversation_type(self, question: str) -> str:
        """Classify the conversation type for context optimization"""
        
        question_lower = question.lower()
        
        # Check for follow-up patterns first (more specific)
        follow_up_patterns = [
            "tiếp tục", "thêm", "chi tiết", "cụ thể", "rõ ràng", "đầy đủ",
            "số liệu", "con số", "dữ liệu", "thông tin", "giải thích thêm",
            "nói thêm", "cho biết thêm", "bổ sung", "mở rộng", "phân tích thêm",
            "đừng chỉ", "không chỉ", "nhiều hơn", "sâu hơn", "rộng hơn",
            "cần thêm", "muốn thêm", "yêu cầu thêm", "làm rõ", "giải thích rõ"
        ]
        
        if any(pattern in question_lower for pattern in follow_up_patterns):
            return "follow_up"
        
        # Check for data analysis patterns
        data_analysis_patterns = [
            "phân tích", "báo cáo", "thống kê", "truy vấn", "bao nhiêu", "số lượng",
            "doanh thu", "lợi nhuận", "tăng trưởng", "giảm", "so sánh", "xu hướng"
        ]
        
        if any(pattern in question_lower for pattern in data_analysis_patterns):
            return "data_analysis"
        
        # Check for explanation patterns
        explanation_patterns = [
            "giải thích", "tại sao", "như thế nào", "vì sao", "làm sao",
            "nguyên nhân", "lý do", "cách thức", "phương pháp"
        ]
        
        if any(pattern in question_lower for pattern in explanation_patterns):
            return "explanation"
        
        # Check for greeting patterns
        greeting_patterns = [
            "xin chào", "chào", "cảm ơn", "hello", "hi", "tạm biệt", "bye"
        ]
        
        if any(pattern in question_lower for pattern in greeting_patterns):
            return "greeting"
        
        return "conversational"
    
    def _get_cubejs_context(self, question: str) -> str:
        """Get CubeJS-specific context using knowledge adapter"""
        try:
            # Use knowledge adapter to retrieve relevant CubeJS knowledge
            knowledge_results = self.knowledge_adapter.retrieve_knowledge(
                query=f"CubeJS {question}",
                limit=5,
                strategy=KnowledgeRetrievalStrategy.HYBRID
            )
            
            context_parts = []
            for result in knowledge_results:
                content = result.get("content", "")
                if content:
                    context_parts.append(content)
            
            return "\n\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.warning(f"Error getting CubeJS context: {e}")
            return ""
    
    def _generate_schema_context(self) -> str:
        """Generate clean schema context based on real CubeJS schema"""
        return """
            🚨 CRITICAL: CubeJS can ONLY query ONE CUBE at a time - NO JOINS allowed!

            AVAILABLE CUBES (query separately for each):

            📊 SALES_METRICS (Dữ liệu bán hàng)
            - Purpose: Sales performance, revenue, customer data
            - Measures: sales_metrics.total_revenue, sales_metrics.total_orders, sales_metrics.new_customers, sales_metrics.customer_visits, sales_metrics.payment_received
            - Dimensions: sales_metrics.sales_channel, sales_metrics.created_at (time)

            💰 FINANCIAL_METRICS (Dữ liệu tài chính)  
            - Purpose: Banking, cash flow, costs, debt ratios
            - Measures: financial_metrics.bank_inflow, financial_metrics.bank_outflow, financial_metrics.cash_balance, financial_metrics.debt_ratio, financial_metrics.energy_cost, financial_metrics.labor_cost, financial_metrics.material_cost
            - Dimensions: financial_metrics.created_at (time)

            🏭 PRODUCTION_METRICS (Dữ liệu sản xuất)
            - Purpose: Production efficiency, labor productivity, manufacturing data
            - Measures: production_metrics.raw_material_volume, production_metrics.finished_product_volume, production_metrics.efficiency_cut, production_metrics.efficiency_aseptic, production_metrics.direct_labor_count
            - Dimensions: production_metrics.company_code, production_metrics.created_at (time)

            👥 HR_METRICS (Dữ liệu nhân sự)
            - Purpose: Employee management, hiring, training
            - Measures: hr_metrics.total_employees, hr_metrics.new_hires, hr_metrics.training_sessions, hr_metrics.applications_received
            - Dimensions: hr_metrics.created_at (time)

            🏢 COMPANIES (Thông tin công ty)
            - Purpose: Company information, departments
            - Measures: companies.count
            - Dimensions: companies.company_name, companies.company_code, companies.department_type, companies.created_at (time)

            📈 EXECUTIVE_DASHBOARD (Tổng quan điều hành)
            - Purpose: High-level business overview, combined metrics
            - Measures: executive_dashboard.total_daily_revenue, executive_dashboard.total_costs, executive_dashboard.operational_efficiency, executive_dashboard.cash_flow_ratio
            - Dimensions: executive_dashboard.report_date (time), executive_dashboard.company_name, executive_dashboard.department_type

            CRITICAL RULES:
            1. ONE CUBE PER QUERY - perform multiple queries if you need data from different cubes
            2. ALWAYS use cube prefix (e.g., "sales_metrics.total_revenue", NOT "total_revenue")
            3. Field names are case-sensitive and must match exactly
            4. Use appropriate cube based on question topic
            5. For time dimensions, use "created_at" for most cubes, "report_date" for executive_dashboard
        """
    
    def _store_conversation_with_metadata(self, question: str, response: str, enhanced_context: Dict[str, Any]):
        """Store conversation with agentic memory layer management and intelligent summarization"""
        try:
            # Extract metadata from enhanced context
            retrieval_metadata = enhanced_context.get("retrieval_metadata", {})
            conversation_type = retrieval_metadata.get("conversation_type", "unknown")
            
            # ALWAYS store current conversation in IN_SESSION layer
            self._store_current_conversation(question, response, conversation_type, retrieval_metadata)
            
            # Use Memory Decision Agent for intelligent storage decisions
            print(f"🧠 Using Memory Decision Agent for intelligent storage decisions...")
            memory_decisions = self.memory_decision_agent.analyze_and_decide_memory_storage(
                question=question,
                response=response,
                conversation_type=conversation_type,
                context_metadata=retrieval_metadata
            )
            
            # Log the agent's reasoning
            reasoning = memory_decisions.get("reasoning", "No reasoning provided")
            print(f"🤖 Memory Decision Agent Reasoning:\n{reasoning}")
            
            # Check if this should only be stored in IN_SESSION (operational states)
            storage_decisions = memory_decisions.get("storage_decisions", {})
            if storage_decisions.get("store_in_session_only"):
                print(f"📝 Operational state detected - storing only in IN_SESSION memory")
                return  # Already stored in IN_SESSION, no need for additional storage
            
            # Execute the agent's storage decisions for LONG_TERM and SHORT_TERM
            execution_results = self.memory_decision_agent.execute_memory_decisions(
                question=question,
                response=response,
                memory_decisions=memory_decisions
            )
            
            # Log execution results
            if execution_results.get("long_term_stored"):
                print(f"✅ Stored in LONG-TERM memory (ID: {execution_results.get('long_term_id')})")
            
            if execution_results.get("short_term_stored"):
                print(f"✅ Stored in SHORT-TERM memory (ID: {execution_results.get('short_term_id')})")
            
            if execution_results.get("errors"):
                for error in execution_results["errors"]:
                    print(f"⚠️ Memory storage error: {error}")
            
            # Store the agent's decision metadata for future reference
            self.memory_manager.store_context(
                session_id=self.session_id,
                context_type="memory_decision_log",
                data=f"Memory Decision: {memory_decisions.get('reasoning', 'Unknown')}",
                importance=0.3,
                metadata={
                    "decision_agent": "VietnameseMemoryDecisionAgent",
                    "storage_decisions": memory_decisions.get("storage_decisions", {}),
                    "execution_results": execution_results,
                    "timestamp": datetime.now().isoformat()
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Check if we need to trigger session summarization (keep this logic)
            self._check_and_trigger_session_summarization()
            
        except Exception as e:
            logger.warning(f"Error in agentic memory storage: {e}")
            # Fallback to simple storage in case of agent failure
            self._fallback_simple_storage(question, response, conversation_type, retrieval_metadata)
    
    def _store_current_conversation(self, question: str, response: str, conversation_type: str, retrieval_metadata: Dict[str, Any]):
        """Store current conversation in IN_SESSION memory layer"""
        try:
            # Store user message in IN_SESSION
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="user",
                content=question,
                metadata={
                    "conversation_type": conversation_type,
                    "context_strategy": retrieval_metadata.get("strategy", "unknown"),
                    "domain": "business_intelligence",
                    "language": "vietnamese",
                    "system": "refactored_crew_agent_classes",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.4  # Lower importance for current messages
                },
                memory_layer=MemoryLayer.IN_SESSION  # Explicitly in-session
            )
            
            # Store assistant response in IN_SESSION
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="assistant",
                content=response,
                metadata={
                    "conversation_type": conversation_type,
                    "context_strategy": retrieval_metadata.get("strategy", "unknown"),
                    "domain": "business_intelligence",
                    "language": "vietnamese",
                    "system": "refactored_crew_agent_classes",
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "importance": 0.4  # Lower importance for current messages
                },
                memory_layer=MemoryLayer.IN_SESSION  # Explicitly in-session
            )
            
        except Exception as e:
            logger.warning(f"Error storing current conversation: {e}")
    
    def _check_and_trigger_session_summarization(self):
        """Check if session needs summarization and trigger if needed"""
        try:
            # Get current session message count
            session_contexts = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=50,  # Get more messages to count properly
                include_layers=[MemoryLayer.IN_SESSION]
            )
            
            # Count actual messages (those with 'role' field indicating user/assistant messages)
            message_count = 0
            for ctx in session_contexts:
                try:
                    # Parse the data field to check for role
                    data_str = ctx.get("data", "{}")
                    if isinstance(data_str, str):
                        data = json.loads(data_str)
                        if data.get("role") in ["user", "assistant"]:
                            message_count += 1
                    elif isinstance(data_str, dict) and data_str.get("role") in ["user", "assistant"]:
                        message_count += 1
                except (json.JSONDecodeError, AttributeError):
                    # Fallback: check if it has role directly
                    if ctx.get("role") in ["user", "assistant"]:
                        message_count += 1
            
            # Trigger summarization every 10 messages
            if message_count > 0 and message_count % 10 == 0:
                logger.info(f"🔄 Triggering session summarization at {message_count} messages")
                self.trigger_manual_summarization()
                
        except Exception as e:
            logger.warning(f"Error checking session summarization: {e}")
    
    def _fallback_simple_storage(self, question: str, response: str, conversation_type: str, retrieval_metadata: Dict[str, Any]):
        """Fallback to simple storage logic if agentic system fails"""
        try:
            logger.info("🔄 Using fallback simple storage logic")
            
            # Simple rules for fallback
            response_lower = response.lower()
            
            # Store in short-term if contains BI keywords
            bi_keywords = ["doanh thu", "lợi nhuận", "phân tích", "báo cáo", "thống kê"]
            if any(keyword in response_lower for keyword in bi_keywords):
                summary = f"Fallback Summary: {question[:100]} | {response[:150]}"
                self.memory_manager.store_context(
                    session_id=self.session_id,
                    context_type="fallback_summary",
                    data=summary,
                    importance=0.5,
                    metadata={
                        "storage_type": "fallback",
                        "conversation_type": conversation_type,
                        "timestamp": datetime.now().isoformat()
                    },
                    memory_layer=MemoryLayer.SHORT_TERM
                )
                print("✅ Fallback: Stored in SHORT-TERM memory")
            
            # Store in long-term if substantial analysis
            if conversation_type == "data_analysis" and len(response) > 200:
                insight = f"Fallback Insight: {conversation_type} analysis - {question[:50]}"
                self.memory_manager.store_context(
                    session_id=self.session_id,
                    context_type="fallback_insight",
                    data=insight,
                    importance=0.7,
                    metadata={
                        "storage_type": "fallback",
                        "conversation_type": conversation_type,
                        "timestamp": datetime.now().isoformat()
                    },
                    memory_layer=MemoryLayer.LONG_TERM
                )
                print("✅ Fallback: Stored in LONG-TERM memory")
                
        except Exception as e:
            logger.warning(f"Error in fallback storage: {e}")
    
    def _create_session_summary(self, recent_messages: List[Dict[str, Any]]):
        """Create a summary of recent session activity"""
        try:
            # Extract conversation types and topics
            conversation_types = []
            topics = []
            
            for msg in recent_messages:
                metadata = msg.get("metadata", {})
                conv_type = metadata.get("conversation_type", "unknown")
                if conv_type not in conversation_types:
                    conversation_types.append(conv_type)
            
            # Create session summary
            summary = f"Tóm tắt phiên làm việc: {len(recent_messages)} tin nhắn, " \
                     f"các loại hội thoại: {', '.join(conversation_types)}"
            
            # Store in SHORT_TERM layer
            self.memory_manager.store_context(
                session_id=self.session_id,
                context_type="session_summary",
                data=summary,
                importance=0.5,
                metadata={
                    "summary_type": "session",
                    "message_count": len(recent_messages),
                    "conversation_types": conversation_types,
                    "timestamp": datetime.now().isoformat(),
                    "domain": "business_intelligence",
                    "system": "refactored_crew_agent_classes"
                },
                memory_layer=MemoryLayer.SHORT_TERM
            )
            
        except Exception as e:
            logger.warning(f"Error creating session summary: {e}")

    def _format_enhanced_context_for_agents(self, enhanced_context: Dict[str, Any]) -> str:
        """Format enhanced context for agent backstories with proper memory layer separation"""
        
        context_parts = []
        
        # Add context type information
        context_type = enhanced_context.get("context_type", "unknown")
        retrieval_metadata = enhanced_context.get("retrieval_metadata", {})
        
        context_parts.append(f"MEMORY CONTEXT RETRIEVAL INFO:")
        context_parts.append(f"- Strategy: {retrieval_metadata.get('strategy', 'unknown')}")
        context_parts.append(f"- Context Type: {context_type}")
        context_parts.append(f"- Used Short-term: {retrieval_metadata.get('used_short_term', False)}")
        context_parts.append(f"- Used Long-term: {retrieval_metadata.get('used_long_term', False)}")
        context_parts.append("")
        
        # Format IN-MEMORY context (always present)
        in_memory_context = enhanced_context.get("in_memory_context", [])
        if in_memory_context:
            context_parts.append("CURRENT CONVERSATION (In-Memory):")
            for msg in in_memory_context[-5:]:  # Last 5 messages
                try:
                    # Parse the data field which contains the actual message content
                    data_str = msg.get("data", "{}")
                    if isinstance(data_str, str):
                        data = json.loads(data_str)
                    else:
                        data = data_str
                    
                    role = data.get("role", "unknown")
                    content = data.get("content", "")
                    timestamp = data.get("timestamp", "")
                    
                    if content:
                        context_parts.append(f"- {role.upper()}: {content[:200]}...")
                        if timestamp:
                            context_parts.append(f"  (Time: {timestamp})")
                except (json.JSONDecodeError, AttributeError) as e:
                    # Fallback to old method if parsing fails
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    if content:
                        context_parts.append(f"- {role.upper()}: {content[:200]}...")
            context_parts.append("")
        
        # Format SHORT-TERM summaries (if retrieved)
        short_term_summaries = enhanced_context.get("short_term_summaries", [])
        if short_term_summaries:
            context_parts.append("RECENT SESSION SUMMARIES (Short-term Memory - Enhanced Semantic Search):")
            for summary in short_term_summaries:
                content = summary.get("content", "")
                summary_type = summary.get("summary_type", "unknown")
                topics = summary.get("topics", [])
                importance = summary.get("importance", 0.0)
                similarity_score = summary.get("similarity_score", 0.0)
                search_method = summary.get("search_method", "unknown")
                relevance_reason = summary.get("relevance_reason", "")
                
                if content:
                    # Enhanced formatting with similarity and search method
                    method_emoji = "🧠" if "semantic" in search_method else "📝"
                    context_parts.append(f"- {method_emoji} [{summary_type}] (Similarity: {similarity_score:.2f}, Importance: {importance:.2f}): {content[:150]}...")
                    if topics:
                        context_parts.append(f"  └─ Topics: {', '.join(topics)}")
                    if relevance_reason:
                        context_parts.append(f"  └─ Relevance: {relevance_reason}")
                    context_parts.append(f"  └─ Search Method: {search_method}")
            context_parts.append("")
        
        # Format LONG-TERM insights (if retrieved)
        long_term_insights = enhanced_context.get("long_term_insights", [])
        if long_term_insights:
            context_parts.append("HISTORICAL INSIGHTS (Long-term Memory - Enhanced Semantic Search):")
            for insight in long_term_insights:
                content = insight.get("content", "")
                insight_type = insight.get("insight_type", "unknown")
                importance = insight.get("importance", 0.0)
                cross_session = insight.get("cross_session", False)
                similarity_score = insight.get("similarity_score", 0.0)
                search_method = insight.get("search_method", "unknown")
                relevance_reason = insight.get("relevance_reason", "")
                domain = insight.get("domain", "unknown")
                
                if content:
                    # Enhanced formatting with similarity and cross-session indicators
                    method_emoji = "🧠" if "semantic" in search_method else "📝"
                    session_indicator = " [Cross-session]" if cross_session else " [Same session]"
                    context_parts.append(f"- {method_emoji} [{insight_type}] (Similarity: {similarity_score:.2f}, Importance: {importance:.2f}){session_indicator}: {content[:150]}...")
                    if domain != "unknown":
                        context_parts.append(f"  └─ Domain: {domain}")
                    if relevance_reason:
                        context_parts.append(f"  └─ Relevance: {relevance_reason}")
                    context_parts.append(f"  └─ Search Method: {search_method}")
            context_parts.append("")
        
        # Format knowledge context (always available)
        knowledge_context = enhanced_context.get("knowledge_context", "")
        if knowledge_context:
            context_parts.append("CUBEJS KNOWLEDGE BASE:")
            # Truncate knowledge context to prevent overwhelming agents
            truncated_knowledge = knowledge_context[:500] + "..." if len(knowledge_context) > 500 else knowledge_context
            context_parts.append(truncated_knowledge)
            context_parts.append("")
        
        # Add memory layer usage instructions
        context_parts.append("ENHANCED MEMORY LAYER USAGE GUIDE:")
        context_parts.append("- IN-MEMORY: Current conversation context (always available)")
        if short_term_summaries:
            context_parts.append("- SHORT-TERM: Session summaries and recent insights (semantic search with similarity scoring)")
        if long_term_insights:
            context_parts.append("- LONG-TERM: Important cross-session insights (enhanced semantic search with cross-session capabilities)")
        context_parts.append("- KNOWLEDGE: CubeJS documentation and schemas (always available)")
        context_parts.append("")
        
        # Add context usage instructions
        context_parts.append("CONTEXT USAGE INSTRUCTIONS:")
        context_parts.append("- Prioritize in-memory context for conversation continuity")
        context_parts.append("- Use short-term summaries to understand recent session patterns")
        context_parts.append("- Reference long-term insights for complex analysis and historical patterns")
        context_parts.append("- Always use knowledge base for accurate CubeJS technical details")
        context_parts.append("- Mention when you're using insights from previous sessions")
        
        # Add enhanced context usage instructions
        context_parts.append("ENHANCED CONTEXT USAGE INSTRUCTIONS:")
        context_parts.append("- Prioritize in-memory context for conversation continuity")
        context_parts.append("- Use short-term summaries with high similarity scores (>0.5) for recent session patterns")
        context_parts.append("- Reference long-term insights with high similarity scores (>0.6) for complex analysis and historical patterns")
        context_parts.append("- Pay attention to relevance reasons to understand why context was retrieved")
        context_parts.append("- Cross-session insights provide valuable historical perspective")
        context_parts.append("- Always use knowledge base for accurate CubeJS technical details")
        context_parts.append("- Mention when you're using insights from previous sessions or semantic matches")
        context_parts.append("- Higher similarity scores indicate more relevant context")
        context_parts.append("")
        
        # Add semantic search metadata
        if short_term_summaries or long_term_insights:
            context_parts.append("SEMANTIC SEARCH METADATA:")
            if short_term_summaries:
                avg_short_similarity = sum(s.get("similarity_score", 0.0) for s in short_term_summaries) / len(short_term_summaries)
                context_parts.append(f"- Short-term average similarity: {avg_short_similarity:.2f}")
            if long_term_insights:
                avg_long_similarity = sum(i.get("similarity_score", 0.0) for i in long_term_insights) / len(long_term_insights)
                cross_session_count = sum(1 for i in long_term_insights if i.get("cross_session", False))
                context_parts.append(f"- Long-term average similarity: {avg_long_similarity:.2f}")
                context_parts.append(f"- Cross-session insights: {cross_session_count}/{len(long_term_insights)}")
            context_parts.append("")
        
        formatted_context = "\n".join(context_parts)
        
        # Log context summary for debugging
        logger.info(f"Formatted selective context: {len(in_memory_context)} in-memory messages, "
                   f"{len(short_term_summaries)} short-term summaries, "
                   f"{len(long_term_insights)} long-term insights")
        
        return formatted_context

    def _get_fallback_enhanced_context(self, question: str, strategy: ContextRetrievalStrategy) -> Dict[str, Any]:
        """Get enhanced context using fallback methods with proper memory layer separation"""
        try:
            # Always get in-memory context
            in_memory_context = self._get_in_memory_context()
            
            # Get minimal short-term context for fallback
            short_term_context = []
            try:
                short_term_context = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query=question,
                    context_types=["conversation_summary"],
                    limit=2,
                    include_layers=[MemoryLayer.SHORT_TERM],
                    cross_session=False
                )
            except Exception as e:
                logger.warning(f"Error in fallback short-term retrieval: {e}")
            
            # Get knowledge context using knowledge adapter
            knowledge_context = ""
            try:
                if hasattr(self, 'knowledge_adapter') and self.knowledge_adapter:
                    knowledge_results = self.knowledge_adapter.retrieve_knowledge(
                        query=f"CubeJS {question}",
                        limit=2
                    )
                    
                    knowledge_parts = []
                    for result in knowledge_results:
                        content = result.get("content", "")
                        if content:
                            knowledge_parts.append(content[:200])
                    knowledge_context = "\n".join(knowledge_parts)
            except Exception as e:
                logger.warning(f"Error getting knowledge context: {e}")
            
            return {
                "in_memory_context": in_memory_context,
                "short_term_summaries": [
                    {
                        "type": "short_term_summary",
                        "content": item.get("data", ""),
                        "summary_type": item.get("metadata", {}).get("context_type", "unknown"),
                        "timestamp": item.get("metadata", {}).get("timestamp", ""),
                        "importance": item.get("metadata", {}).get("importance", 0.0)
                    }
                    for item in short_term_context
                ],
                "long_term_insights": [],  # No long-term in fallback
                "knowledge_context": knowledge_context,
                "context_type": "fallback_selective",
                "retrieval_metadata": {
                    "strategy": strategy.value if hasattr(strategy, 'value') else str(strategy),
                    "conversation_type": self._classify_conversation_type(question),
                    "used_short_term": len(short_term_context) > 0,
                    "used_long_term": False,
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "fallback_used": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fallback context retrieval: {e}")
            return self._get_minimal_context(question)

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get enhanced memory statistics with layer breakdown"""
        try:
            base_stats = {
                "session_id": self.session_id,
                "memory_backend": "Golett with Selective Layer Retrieval",
                "agent_classes": "Active",
                "task_factory": "Active",
                "knowledge_adapter": "Active",
                "version": "refactored_agent_classes_selective_memory",
                "architecture": "selective_memory_layers"
            }
            
            # Get session info
            session_info = self.session_manager.get_session_info(self.session_id)
            if session_info:
                base_stats["session_info"] = session_info
            
            # Get conversation count by layer
            in_memory_history = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=100,
                include_layers=[MemoryLayer.IN_SESSION]
            )
            
            short_term_history = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=100,
                include_layers=[MemoryLayer.SHORT_TERM]
            )
            
            long_term_history = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=100,
                include_layers=[MemoryLayer.LONG_TERM]
            )
            
            base_stats["memory_layer_stats"] = {
                "in_memory_messages": len(in_memory_history),
                "short_term_summaries": len(short_term_history),
                "long_term_insights": len(long_term_history),
                "total_items": len(in_memory_history) + len(short_term_history) + len(long_term_history)
            }
            
            # Get agent class information
            base_stats["agent_classes_count"] = 5
            base_stats["agent_class_names"] = [
                "VietnameseDataAnalystAgent",
                "VietnameseConversationClassifierAgent", 
                "VietnameseFollowUpAgent",
                "VietnameseConversationalAgent",
                "VietnameseExplanationAgent"
            ]
            
            # Get knowledge collections
            collections = self.knowledge_adapter.list_collections()
            base_stats["knowledge_collections"] = len(collections)
            
            # Memory layer configuration
            base_stats["memory_layer_config"] = {
                "in_memory": "Current conversation (always used)",
                "short_term": "Session summaries (selective retrieval)",
                "long_term": "Cross-session insights (complex analysis only)",
                "summarization": "Automatic every 10 messages"
            }
            
            return base_stats
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}
    
    def trigger_manual_summarization(self) -> Dict[str, Any]:
        """Manually trigger summarization for testing purposes"""
        try:
            # Get recent messages
            recent_messages = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=10,
                include_layers=[MemoryLayer.IN_SESSION]
            )
            
            if len(recent_messages) < 2:
                return {
                    "status": "skipped",
                    "message": "Not enough messages to summarize",
                    "message_count": len(recent_messages)
                }
            
            # Create session summary
            self._create_session_summary(recent_messages)
            
            # Create conversation summaries for recent data analysis
            summary_count = 0
            insight_count = 0
            
            for msg in recent_messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    metadata = msg.get("metadata", {})
                    conversation_type = metadata.get("conversation_type", "unknown")
                    
                    # Find corresponding user question
                    user_question = "Manual summarization"
                    for prev_msg in recent_messages:
                        if (prev_msg.get("role") == "user" and 
                            prev_msg.get("metadata", {}).get("timestamp", "") < metadata.get("timestamp", "")):
                            user_question = prev_msg.get("content", "")
                            break
                    
                    # Create summaries
                    if self._should_create_short_term_summary(conversation_type, content):
                        self._create_and_store_short_term_summary(user_question, content, conversation_type)
                        summary_count += 1
                    
                    if self._should_create_long_term_insight(conversation_type, content):
                        self._create_and_store_long_term_insight(user_question, content, conversation_type)
                        insight_count += 1
            
            return {
                "status": "success",
                "message": f"Manual summarization completed",
                "processed_messages": len(recent_messages),
                "short_term_summaries_created": summary_count,
                "long_term_insights_created": insight_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in manual summarization: {e}")
            return {
                "status": "error",
                "message": f"Error during manual summarization: {str(e)}"
            }
    
    def get_memory_layer_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of memory layer contents"""
        try:
            breakdown = {}
            
            for layer in [MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]:
                try:
                    # Get items from this layer
                    items = self.memory_manager.get_session_history(
                        session_id=self.session_id,
                        limit=50,
                        include_layers=[layer]
                    )
                    
                    # Analyze content types
                    content_types = {}
                    for item in items:
                        content_type = item.get("metadata", {}).get("type", "unknown")
                        if content_type not in content_types:
                            content_types[content_type] = 0
                        content_types[content_type] += 1
                    
                    breakdown[layer.value] = {
                        "total_items": len(items),
                        "content_types": content_types,
                        "sample_items": [
                            {
                                "type": item.get("metadata", {}).get("type", "unknown"),
                                "content": item.get("content", "")[:100] + "..." if len(item.get("content", "")) > 100 else item.get("content", ""),
                                "timestamp": item.get("metadata", {}).get("timestamp", "")
                            }
                            for item in items[:3]  # First 3 items as samples
                        ]
                    }
                    
                except Exception as e:
                    breakdown[layer.value] = {"error": str(e)}
            
            return {
                "session_id": self.session_id,
                "breakdown": breakdown,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting memory layer breakdown: {e}")
            return {"error": str(e)}

    def _determine_relevance_reason(self, question: str, content: str) -> str:
        """Determine why a memory item is relevant to the current question"""
        try:
            question_lower = question.lower()
            content_lower = str(content).lower()
            
            # Check for direct keyword matches
            question_words = set(question_lower.split())
            content_words = set(content_lower.split())
            common_words = question_words.intersection(content_words)
            
            # Filter out common Vietnamese stop words
            stop_words = {'của', 'và', 'với', 'cho', 'từ', 'về', 'trong', 'trên', 'dưới', 'này', 'đó', 'là', 'có', 'được'}
            meaningful_common = common_words - stop_words
            
            if len(meaningful_common) >= 2:
                return f"Keyword matches: {', '.join(list(meaningful_common)[:3])}"
            
            # Check for business domain matches
            business_domains = {
                'doanh thu': 'revenue analysis',
                'bán hàng': 'sales data', 
                'tài chính': 'financial metrics',
                'khách hàng': 'customer insights',
                'sản phẩm': 'product analysis',
                'nhân viên': 'employee data',
                'chi phí': 'cost analysis',
                'lợi nhuận': 'profit analysis'
            }
            
            for domain_vn, domain_en in business_domains.items():
                if domain_vn in question_lower and domain_vn in content_lower:
                    return f"Business domain: {domain_en}"
            
            # Check for analysis type matches
            analysis_types = {
                'phân tích': 'analysis request',
                'báo cáo': 'reporting',
                'thống kê': 'statistics',
                'so sánh': 'comparison',
                'xu hướng': 'trend analysis',
                'tăng trưởng': 'growth analysis'
            }
            
            for analysis_vn, analysis_en in analysis_types.items():
                if analysis_vn in question_lower and analysis_vn in content_lower:
                    return f"Analysis type: {analysis_en}"
            
            # Check for time-related matches
            time_indicators = ['tháng', 'năm', 'quý', 'tuần', 'ngày', 'hôm nay', 'hôm qua']
            question_has_time = any(time_word in question_lower for time_word in time_indicators)
            content_has_time = any(time_word in content_lower for time_word in time_indicators)
            
            if question_has_time and content_has_time:
                return "Temporal relevance"
            
            # Check for numerical/data relevance
            import re
            question_has_numbers = bool(re.search(r'\d+', question))
            content_has_numbers = bool(re.search(r'\d+', content))
            
            if question_has_numbers and content_has_numbers:
                return "Numerical data relevance"
            
            # Default semantic relevance
            if len(meaningful_common) > 0:
                return f"Semantic similarity: {', '.join(list(meaningful_common)[:2])}"
            
            return "Semantic vector similarity"
            
        except Exception as e:
            logger.warning(f"Error determining relevance reason: {e}")
            return "Unknown relevance"


def main():
    """Start the interactive refactored Vietnamese chatbot with agent classes"""
    print("🚀 Starting Refactored Vietnamese Business Intelligence Chatbot with Agent Classes...")
    print("🔧 Enhanced with proper agent and task class separation")
    
    # Get environment variables
    postgres_connection = os.getenv("POSTGRES_CONNECTION")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    if not postgres_connection:
        print("❌ POSTGRES_CONNECTION environment variable is required")
        print("💡 Example: export POSTGRES_CONNECTION='postgresql://user:password@localhost:5432/golett_db'")
        return
    
    try:
        # Initialize refactored chatbot with agent classes
        chatbot = RefactoredVietnameseCubeJSChatbot(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            cubejs_api_url=cubejs_api_url,
            cubejs_api_token=cubejs_api_token,
            user_id="interactive_user_refactored_agent_classes"
        )
        
        # Test connection
        connection_test = chatbot.test_connection()
        print(f"📡 {connection_test['message']}")
        
        if connection_test["status"] == "error":
            print("❌ Cannot start chat without proper connections")
            return
        
        # Show enhanced memory stats
        memory_stats = chatbot.get_memory_stats()
        print(f"🧠 Memory Backend: {memory_stats.get('memory_backend', 'Unknown')}")
        print(f"📱 Session ID: {chatbot.session_id}")
        print(f"🏗️ Architecture: {memory_stats.get('architecture', 'Unknown')}")
        print(f"👥 Agent Classes: {memory_stats.get('agent_classes_count', 0)}")
        print(f"📚 Knowledge Collections: {memory_stats.get('knowledge_collections', 0)}")
        
        print("\n" + "=" * 70)
        print("💬 Refactored Vietnamese BI Chatbot with Agent Classes Ready!")
        print("🔧 Features: Agent Classes | Task Factory | Enhanced Context | Cross-Session Learning")
        print("Type your questions in Vietnamese or 'exit' to quit")
        print("=" * 70)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\n🤔 Câu hỏi của bạn: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'thoát']:
                    print("\n👋 Cảm ơn bạn đã sử dụng chatbot refactored với agent classes!")
                    break
                
                if not user_input:
                    continue
                
                # Process the question
                print(f"\n🤖 Đang xử lý với agent classes và task factory...")
                answer = chatbot.ask(user_input)
                print(f"\n💡 **Trả lời (Agent Classes):**\n{answer}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Lỗi: {str(e)}")

    except Exception as e:
        print(f"❌ Error starting refactored chatbot with agent classes: {str(e)}")

if __name__ == "__main__":
    main()