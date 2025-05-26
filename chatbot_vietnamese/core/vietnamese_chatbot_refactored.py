#!/usr/bin/env python3
"""
Refactored Vietnamese Business Intelligence Chatbot with Crew and Enhanced Context Manager

This refactored version uses Golett's latest capabilities:
- CrewChatSession and CrewChatFlowManager for crew-based conversation management
- EnhancedContextManager for sophisticated context retrieval
- GolettKnowledgeAdapter for knowledge management
- Clean, modern architecture using Golett's crew system
- Proper separation of agents and tasks into dedicated modules
"""

import os
import sys
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, Process

# Golett core imports - updated to use crew system
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.session.session_manager import SessionManager
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
        from golett.memory.contextual.context_manager import ContextManager
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
            valid_types = ["data_analysis", "follow_up", "conversational", "clarification"]
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
        """Get enhanced context using the enhanced context manager with proper fallback"""
        
        try:
            # Determine the appropriate context retrieval strategy
            strategy = self._determine_context_strategy(question)
            
            # Try to get enhanced context if enhanced context manager is available
            if hasattr(self, 'enhanced_context_manager') and self.enhanced_context_manager:
                try:
                    enhanced_context = self.enhanced_context_manager.get_enhanced_context(
                        session_id=self.session_id,
                        question=question,
                        strategy=strategy,
                        domain="business_intelligence",
                        conversation_type=self._classify_conversation_type(question),
                        include_cross_session=True,
                        max_context_age_days=30
                    )
                    
                    # If we got valid context, return it
                    if enhanced_context and enhanced_context.get("context_type") != "fallback":
                        return enhanced_context
                        
                except Exception as e:
                    logger.warning(f"Enhanced context manager failed: {e}")
            
            # Fallback to manual context retrieval using basic MemoryManager methods
            logger.info("Using fallback context retrieval")
            return self._get_fallback_enhanced_context(question, strategy)
            
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return self._get_minimal_context(question)
    
    def _get_fallback_enhanced_context(self, question: str, strategy: ContextRetrievalStrategy) -> Dict[str, Any]:
        """Get enhanced context using fallback methods when enhanced context manager fails"""
        try:
            # Get recent conversation history
            recent_conversation = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=5,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            # Get semantic memories using memory manager search
            semantic_memories = []
            try:
                search_results = self.memory_manager.search_message_history(
                    query=question,
                    session_id=self.session_id,
                    limit=3,
                    semantic=True,
                    include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
                )
                
                for result in search_results:
                    semantic_memories.append({
                        "content": result.get("data", ""),
                        "metadata": result.get("metadata", {}),
                        "similarity_score": result.get("score", 0.0),
                        "memory_layer": result.get("metadata", {}).get("searched_in_layer", "unknown"),
                        "timestamp": result.get("metadata", {}).get("timestamp", ""),
                        "context_type": result.get("metadata", {}).get("type", "general")
                    })
            except Exception as e:
                logger.warning(f"Error in semantic search: {e}")
            
            # Get cross-session insights using context retrieval
            cross_session_insights = []
            try:
                if strategy in [ContextRetrievalStrategy.COMPREHENSIVE, ContextRetrievalStrategy.CONTEXTUAL]:
                    context_results = self.memory_manager.retrieve_context(
                        session_id=self.session_id,
                        query=question,
                        context_types=["insight", "bi_data", "knowledge"],
                        limit=3,
                        include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
                        cross_session=True
                    )
                    
                    for result in context_results:
                        cross_session_insights.append({
                            "insight": result.get("data", ""),
                            "source_session": result.get("metadata", {}).get("session_id", "unknown"),
                            "importance": result.get("importance", 0.0),
                            "timestamp": result.get("metadata", {}).get("timestamp", ""),
                            "context_type": result.get("metadata", {}).get("type", "unknown")
                        })
            except Exception as e:
                logger.warning(f"Error getting cross-session insights: {e}")
            
            # Get knowledge context using knowledge adapter
            knowledge_context = []
            try:
                if hasattr(self, 'knowledge_adapter') and self.knowledge_adapter:
                    knowledge_results = self.knowledge_adapter.retrieve_knowledge(
                        query=f"CubeJS {question}",
                        limit=3
                    )
                    
                    for result in knowledge_results:
                        knowledge_context.append({
                            "content": result.get("content", ""),
                            "source": result.get("source", "unknown"),
                            "relevance": result.get("relevance", 0.0)
                        })
            except Exception as e:
                logger.warning(f"Error getting knowledge context: {e}")
            
            return {
                "recent_conversation": recent_conversation,
                "semantic_memories": semantic_memories,
                "cross_session_insights": cross_session_insights,
                "knowledge_context": knowledge_context,
                "context_type": "fallback_enhanced",
                "retrieval_metadata": {
                    "strategy": strategy.value,
                    "domain": "business_intelligence",
                    "conversation_type": self._classify_conversation_type(question),
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "fallback_used": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fallback context retrieval: {e}")
            return self._get_minimal_context(question)
    
    def _get_minimal_context(self, question: str) -> Dict[str, Any]:
        """Get minimal context when all else fails"""
        try:
            # Just get recent conversation history
            recent_conversation = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=3,
                include_layers=[MemoryLayer.IN_SESSION]
            )
            
            return {
                "recent_conversation": recent_conversation,
                "semantic_memories": [],
                "cross_session_insights": [],
                "knowledge_context": [],
                "context_type": "minimal",
                "retrieval_metadata": {
                    "strategy": "minimal",
                    "domain": "business_intelligence",
                    "conversation_type": self._classify_conversation_type(question),
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "minimal_fallback": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in minimal context retrieval: {e}")
            return {
                "recent_conversation": [],
                "semantic_memories": [],
                "cross_session_insights": [],
                "knowledge_context": [],
                "context_type": "error",
                "error": str(e),
                "retrieval_metadata": {
                    "strategy": "error",
                    "domain": "business_intelligence",
                    "conversation_type": "unknown",
                    "retrieved_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "error": str(e)
                }
            }
    
    def _determine_context_strategy(self, question: str) -> ContextRetrievalStrategy:
        """Determine the appropriate context retrieval strategy based on the question"""
        
        question_lower = question.lower()
        
        # Data analysis questions need comprehensive context
        if any(keyword in question_lower for keyword in [
            "phân tích", "dữ liệu", "báo cáo", "thống kê", "doanh thu", "lợi nhuận", "bao nhiêu"
        ]):
            return ContextRetrievalStrategy.COMPREHENSIVE
        
        # Follow-up questions need contextual strategy
        if any(keyword in question_lower for keyword in [
            "tiếp tục", "thêm", "chi tiết", "giải thích", "tại sao", "vì sao"
        ]):
            return ContextRetrievalStrategy.CONTEXTUAL
        
        # Greetings and casual conversation
        if any(keyword in question_lower for keyword in [
            "xin chào", "chào", "cảm ơn", "tạm biệt", "hello", "hi"
        ]):
            return ContextRetrievalStrategy.CONVERSATIONAL
        
        # Default to focused strategy
        return ContextRetrievalStrategy.FOCUSED
    
    def _classify_conversation_type(self, question: str) -> str:
        """Classify the conversation type for context optimization"""
        
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in [
            "phân tích", "dữ liệu", "báo cáo", "thống kê", "truy vấn", "bao nhiêu", "số lượng"
        ]):
            return "data_analysis"
        
        if any(keyword in question_lower for keyword in [
            "tiếp tục", "thêm", "chi tiết"
        ]):
            return "follow_up"
        
        if any(keyword in question_lower for keyword in [
            "giải thích", "tại sao", "như thế nào", "vì sao"
        ]):
            return "explanation"
        
        if any(keyword in question_lower for keyword in [
            "xin chào", "chào", "cảm ơn", "hello"
        ]):
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
        """Store conversation with enhanced metadata using proper MemoryManager methods"""
        try:
            # Extract metadata from enhanced context
            retrieval_metadata = enhanced_context.get("retrieval_metadata", {})
            
            # Store user message
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="user",
                content=question,
                metadata={
                    "conversation_type": retrieval_metadata.get("conversation_type", "unknown"),
                    "context_strategy": retrieval_metadata.get("strategy", "unknown"),
                    "domain": retrieval_metadata.get("domain", "business_intelligence"),
                    "language": "vietnamese",
                    "system": "refactored_crew_agent_classes",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.6
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Store assistant response
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="assistant",
                content=response,
                metadata={
                    "conversation_type": retrieval_metadata.get("conversation_type", "unknown"),
                    "context_strategy": retrieval_metadata.get("strategy", "unknown"),
                    "domain": retrieval_metadata.get("domain", "business_intelligence"),
                    "language": "vietnamese",
                    "system": "refactored_crew_agent_classes",
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "context_sources": {
                        "semantic_memories": len(enhanced_context.get("semantic_memories", [])),
                        "cross_session_insights": len(enhanced_context.get("cross_session_insights", [])),
                        "related_summaries": len(enhanced_context.get("related_summaries", []))
                    },
                    "importance": 0.7
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Store insights if this was a data analysis conversation
            if retrieval_metadata.get("conversation_type") == "data_analysis":
                self._extract_and_store_insights(question, response)
            
        except Exception as e:
            logger.warning(f"Error storing conversation with metadata: {e}")
    
    def _extract_and_store_insights(self, question: str, response: str):
        """Extract and store insights from data analysis conversations using proper MemoryManager methods"""
        try:
            # Simple insight extraction (could be enhanced with NLP)
            insights = []
            
            response_lower = response.lower()
            if "tăng" in response_lower or "giảm" in response_lower:
                insights.append("trend_analysis")
            
            if "%" in response or "phần trăm" in response_lower:
                insights.append("percentage_analysis")
            
            if "so sánh" in response_lower or "comparison" in response_lower:
                insights.append("comparative_analysis")
            
            # Store insights using store_context method
            for insight in insights:
                self.memory_manager.store_context(
                    session_id=self.session_id,
                    context_type="insight",
                    data={
                        "insight_type": insight,
                        "description": f"Insight from question: {question[:100]}...",
                        "question": question,
                        "response": response[:200],
                        "timestamp": datetime.now().isoformat()
                    },
                    importance=0.6,
                    metadata={
                        "insight_type": insight,
                        "domain": "business_intelligence",
                        "language": "vietnamese",
                        "system": "refactored_crew_agent_classes"
                    },
                    memory_layer=MemoryLayer.SHORT_TERM
                )
            
        except Exception as e:
            logger.warning(f"Error extracting insights: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get enhanced memory statistics"""
        try:
            base_stats = {
                "session_id": self.session_id,
                "memory_backend": "Golett with Enhanced Context Manager",
                "agent_classes": "Active",
                "task_factory": "Active",
                "knowledge_adapter": "Active",
                "version": "refactored_agent_classes",
                "architecture": "agent_task_classes"
            }
            
            # Get session info
            session_info = self.session_manager.get_session_info(self.session_id)
            if session_info:
                base_stats["session_info"] = session_info
            
            # Get conversation count
            history = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=100
            )
            base_stats["conversation_count"] = len(history)
            
            # Get agent class information
            base_stats["agent_classes_count"] = 5  # We have 5 agent classes
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
            
            return base_stats
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history from Golett memory"""
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
                session_type="vietnamese_bi_refactored_agent_classes",
                preferences={
                    "language": "vietnamese", 
                    "domain": "business_intelligence",
                    "version": "refactored_agent_classes"
                }
            )
            
            logger.info(f"🧹 Session memory cleared, new session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test CubeJS connection and enhanced Golett memory system with agent classes"""
        try:
            result = {
                "status": "success",
                "message": "✅ All systems connected",
                "systems": {}
            }
            
            # Test memory manager
            try:
                self.memory_manager.get_session_history(self.session_id, limit=1)
                result["systems"]["memory_manager"] = "✅ Connected"
            except Exception as e:
                result["systems"]["memory_manager"] = f"❌ Error: {e}"
                result["status"] = "error"
            
            # Test enhanced context manager
            try:
                test_context = self.enhanced_context_manager.get_enhanced_context(
                    session_id=self.session_id,
                    question="test",
                    strategy=ContextRetrievalStrategy.CONVERSATIONAL
                )
                result["systems"]["enhanced_context_manager"] = "✅ Connected"
            except Exception as e:
                result["systems"]["enhanced_context_manager"] = f"❌ Error: {e}"
                result["status"] = "error"
            
            # Test agent classes
            try:
                agent_count = len([
                    self.data_analyst_agent_class,
                    self.classifier_agent_class,
                    self.follow_up_agent_class,
                    self.conversational_agent_class,
                    self.explanation_agent_class
                ])
                result["systems"]["agent_classes"] = f"✅ Connected ({agent_count} agent classes)"
            except Exception as e:
                result["systems"]["agent_classes"] = f"❌ Error: {e}"
                result["status"] = "error"
            
            # Test task factory
            try:
                if hasattr(self, 'task_factory') and self.task_factory:
                    result["systems"]["task_factory"] = "✅ Connected"
                else:
                    result["systems"]["task_factory"] = "❌ Not initialized"
                    result["status"] = "error"
            except Exception as e:
                result["systems"]["task_factory"] = f"❌ Error: {e}"
                result["status"] = "error"
            
            # Test knowledge adapter
            try:
                collections = self.knowledge_adapter.list_collections()
                result["systems"]["knowledge_adapter"] = f"✅ Connected ({len(collections)} collections)"
            except Exception as e:
                result["systems"]["knowledge_adapter"] = f"❌ Error: {e}"
                result["status"] = "error"
            
            # Test CubeJS schema
            try:
                schema = self.schema_mapper.refresh_schema()
                if "error" in schema:
                    result["systems"]["cubejs_schema"] = f"❌ Error: {schema['error']}"
                    result["status"] = "error"
                else:
                    result["systems"]["cubejs_schema"] = f"✅ Connected ({schema['total_cubes']} cubes)"
                    result["cubes"] = list(schema["cubes"].keys())
                    result["last_updated"] = schema["last_updated"]
            except Exception as e:
                result["systems"]["cubejs_schema"] = f"❌ Error: {e}"
            
            if result["status"] == "success":
                result["message"] = f"✅ Kết nối thành công! Enhanced Golett Memory with Agent Classes: Active"
            else:
                result["message"] = "⚠️ Some systems have connection issues"
            
            result.update({
                "memory_system": "Enhanced Golett Memory System with Agent Classes",
                "session_id": self.session_id,
                "version": "refactored_agent_classes",
                "architecture": "agent_task_classes",
                "agent_classes": [
                    "VietnameseDataAnalystAgent",
                    "VietnameseConversationClassifierAgent", 
                    "VietnameseFollowUpAgent",
                    "VietnameseConversationalAgent",
                    "VietnameseExplanationAgent"
                ],
                "knowledge_collections": len(self.knowledge_adapter.list_collections())
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"❌ Lỗi kết nối: {str(e)}"
            }

    def _format_enhanced_context_for_agents(self, enhanced_context: Dict[str, Any]) -> str:
        """Format enhanced context for agent backstories with better structure"""
        
        context_parts = []
        
        # Add context type information
        context_type = enhanced_context.get("context_type", "unknown")
        retrieval_metadata = enhanced_context.get("retrieval_metadata", {})
        
        context_parts.append(f"CONTEXT RETRIEVAL INFO:")
        context_parts.append(f"- Strategy: {retrieval_metadata.get('strategy', 'unknown')}")
        context_parts.append(f"- Context Type: {context_type}")
        context_parts.append(f"- Domain: {retrieval_metadata.get('domain', 'unknown')}")
        context_parts.append("")
        
        # Format recent conversation
        recent_conversation = enhanced_context.get("recent_conversation", [])
        if recent_conversation:
            context_parts.append("RECENT CONVERSATION:")
            for msg in recent_conversation[-3:]:  # Last 3 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                timestamp = msg.get("metadata", {}).get("timestamp", "")
                
                if content:
                    context_parts.append(f"- {role.upper()}: {content[:200]}...")
                    if timestamp:
                        context_parts.append(f"  (Time: {timestamp})")
            context_parts.append("")
        
        # Format semantic memories
        semantic_memories = enhanced_context.get("semantic_memories", [])
        if semantic_memories:
            context_parts.append("RELEVANT MEMORIES:")
            for memory in semantic_memories[:3]:  # Top 3 memories
                content = memory.get("content", "")
                score = memory.get("similarity_score", 0.0)
                layer = memory.get("memory_layer", "unknown")
                
                if content:
                    context_parts.append(f"- [{layer}] (Score: {score:.2f}): {content[:150]}...")
            context_parts.append("")
        
        # Format cross-session insights
        cross_session_insights = enhanced_context.get("cross_session_insights", [])
        if cross_session_insights:
            context_parts.append("CROSS-SESSION INSIGHTS:")
            for insight in cross_session_insights[:2]:  # Top 2 insights
                insight_content = insight.get("insight", "")
                importance = insight.get("importance", 0.0)
                source_session = insight.get("source_session", "unknown")
                
                if insight_content:
                    context_parts.append(f"- (Importance: {importance:.2f}, Session: {source_session}): {insight_content[:150]}...")
            context_parts.append("")
        
        # Format knowledge context
        knowledge_context = enhanced_context.get("knowledge_context", [])
        if knowledge_context:
            context_parts.append("KNOWLEDGE BASE:")
            for knowledge in knowledge_context[:2]:  # Top 2 knowledge items
                content = knowledge.get("content", "")
                source = knowledge.get("source", "unknown")
                relevance = knowledge.get("relevance", 0.0)
                
                if content:
                    context_parts.append(f"- [{source}] (Relevance: {relevance:.2f}): {content[:150]}...")
            context_parts.append("")
        
        # Format related summaries if available
        related_summaries = enhanced_context.get("related_summaries", [])
        if related_summaries:
            context_parts.append("RELATED CONVERSATION SUMMARIES:")
            for summary in related_summaries[:2]:  # Top 2 summaries
                summary_content = summary.get("summary", "")
                topics = summary.get("topics", [])
                
                if summary_content:
                    context_parts.append(f"- Topics: {', '.join(topics[:3])}")
                    context_parts.append(f"  Summary: {summary_content[:150]}...")
            context_parts.append("")
        
        # Add domain context if available
        domain_context = enhanced_context.get("domain_context", [])
        if domain_context:
            context_parts.append("DOMAIN-SPECIFIC CONTEXT:")
            for domain_item in domain_context[:2]:  # Top 2 domain items
                content = domain_item.get("content", "")
                context_type = domain_item.get("context_type", "unknown")
                importance = domain_item.get("importance", 0.0)
                
                if content:
                    context_parts.append(f"- [{context_type}] (Importance: {importance:.2f}): {content[:150]}...")
            context_parts.append("")
        
        # Add fallback information if context retrieval had issues
        if context_type in ["fallback_enhanced", "minimal", "error"]:
            context_parts.append("CONTEXT RETRIEVAL NOTES:")
            if context_type == "fallback_enhanced":
                context_parts.append("- Using fallback context retrieval due to enhanced manager issues")
            elif context_type == "minimal":
                context_parts.append("- Using minimal context due to retrieval failures")
            elif context_type == "error":
                error_msg = enhanced_context.get("error", "Unknown error")
                context_parts.append(f"- Context retrieval error: {error_msg}")
            context_parts.append("")
        
        # Add usage instructions
        context_parts.append("CONTEXT USAGE INSTRUCTIONS:")
        context_parts.append("- Use this context to provide more informed and relevant responses")
        context_parts.append("- Reference specific memories or insights when relevant")
        context_parts.append("- Consider conversation history for continuity")
        context_parts.append("- Leverage knowledge base information for accurate technical details")
        
        formatted_context = "\n".join(context_parts)
        
        # Log context summary for debugging
        logger.info(f"Formatted context summary: {len(recent_conversation)} recent messages, "
                   f"{len(semantic_memories)} semantic memories, "
                   f"{len(cross_session_insights)} cross-session insights, "
                   f"{len(knowledge_context)} knowledge items")
        
        return formatted_context


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