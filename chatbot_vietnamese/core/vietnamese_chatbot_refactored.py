#!/usr/bin/env python3
"""
Refactored Vietnamese Business Intelligence Chatbot with Proper Golett Core Integration

This refactored version properly leverages Golett's core capabilities:
- ContextManager for intelligent context retrieval
- Advanced BI context and knowledge integration
- Clean separation of agents and tasks
- Enhanced cross-session learning
"""

import os
import sys
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Crew, Process

# Proper Golett imports
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.session.session_manager import SessionManager
from golett.memory.contextual.context_manager import ContextManager
from golett.knowledge.sources import GolettAdvancedTextFileKnowledgeSource, KnowledgeRetrievalStrategy
from golett.utils.logger import get_logger

# Local imports - using the new modular structure
from chatbot_vietnamese.agents import (
    VietnameseDataAnalystAgent,
    VietnameseConversationClassifierAgent,
    VietnameseFollowUpAgent,
    VietnameseConversationalAgent,
    VietnameseExplanationAgent
)
from chatbot_vietnamese.tasks import VietnameseTaskFactory
from chatbot_vietnamese.utils.dynamic_schema_mapper import DynamicCubeJSSchemaMapper

logger = get_logger(__name__)


class RefactoredVietnameseCubeJSChatbot:
    """
    Refactored Vietnamese Business Intelligence Chatbot with proper Golett core integration
    
    Key improvements:
    - Proper use of Golett's ContextManager for intelligent context retrieval
    - Clean separation of agents and tasks
    - Enhanced business intelligence context management
    - Cross-session knowledge access
    - Modular, maintainable architecture
    """
    
    def __init__(
        self, 
        session_id: str = None,
        user_id: str = "vietnamese_user",
        postgres_connection: str = None,
        qdrant_url: str = "http://localhost:6333",
        cubejs_api_url: str = "http://localhost:4000",
        cubejs_api_token: str = None
    ):
        """
        Initialize Refactored Vietnamese CubeJS Chatbot with proper Golett integration
        
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
        
        # Initialize Golett core system
        logger.info("🔧 Initializing Golett core system...")
        self._initialize_golett_core(postgres_connection, qdrant_url)
        
        # Initialize session
        self._initialize_session(session_id)
        
        # Initialize CubeJS components
        self.schema_mapper = DynamicCubeJSSchemaMapper()
        self.schema_mapper.refresh_schema()
        
        # Initialize knowledge sources
        self.knowledge_sources = self._initialize_knowledge_sources()
        
        # Initialize agents with proper Golett integration
        self._initialize_agents()
        
        # Initialize task factory
        self.task_factory = VietnameseTaskFactory(
            memory_manager=self.memory_manager,
            context_manager=self.context_manager,
            session_id=self.session_id
        )
        
        logger.info(f"✅ Refactored Vietnamese CubeJS Chatbot initialized (session: {self.session_id})")
    
    def _initialize_golett_core(self, postgres_connection: str, qdrant_url: str):
        """Initialize Golett's core memory and context management system"""
        
        # Initialize memory manager with proper configuration
        self.memory_manager = MemoryManager(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            postgres_base_table="vietnamese_chatbot_memories",
            qdrant_base_collection="vietnamese_chatbot_vectors",
            enable_normalized_layers=True
        )
        
        # Initialize session manager
        self.session_manager = SessionManager(self.memory_manager)
        
        # Initialize context manager - this is the key improvement!
        self.context_manager = ContextManager(self.memory_manager)
        
        logger.info("✅ Golett core system initialized")
    
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
                    session_type="vietnamese_bi_refactored",
                    metadata={
                        "session_id": session_id,
                        "version": "refactored",
                        "architecture": "modular"
                    }
                )
        else:
            # Create new session
            self.session_id = self.session_manager.create_session(
                user_id=self.user_id,
                session_type="vietnamese_bi_refactored",
                preferences={
                    "language": "vietnamese", 
                    "domain": "business_intelligence",
                    "version": "refactored"
                }
            )
        
        logger.info(f"✅ Session initialized: {self.session_id}")
    
    def _initialize_knowledge_sources(self) -> Dict[str, Any]:
        """Initialize CubeJS knowledge sources using Golett's knowledge system"""
        knowledge_sources = {}
        
        try:
            # Get the knowledge directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            knowledge_dir = os.path.join(project_root, "knowledge", "cubejs")
            
            # Initialize REST API knowledge source
            rest_api_path = os.path.join(knowledge_dir, "rest_api.md")
            if os.path.exists(rest_api_path):
                rest_api_source = GolettAdvancedTextFileKnowledgeSource(
                    file_path=rest_api_path,
                    memory_manager=self.memory_manager,
                    session_id=self.session_id,
                    collection_name="cubejs_rest_api_refactored",
                    memory_layer=MemoryLayer.LONG_TERM,
                    tags=["cubejs", "rest_api", "query_format", "vietnamese_chatbot", "refactored"],
                    importance=0.9,
                    chunk_size=800,
                    overlap_size=100
                )
                
                rest_api_chunks = rest_api_source.add()
                knowledge_sources["rest_api"] = {
                    "source": rest_api_source,
                    "chunks": len(rest_api_chunks)
                }
                logger.info(f"✅ Loaded CubeJS REST API knowledge: {len(rest_api_chunks)} chunks")
            
            # Initialize schemas knowledge source
            schemas_path = os.path.join(knowledge_dir, "schemas.md")
            if os.path.exists(schemas_path):
                schemas_source = GolettAdvancedTextFileKnowledgeSource(
                    file_path=schemas_path,
                    memory_manager=self.memory_manager,
                    session_id=self.session_id,
                    collection_name="cubejs_schemas_refactored",
                    memory_layer=MemoryLayer.LONG_TERM,
                    tags=["cubejs", "schemas", "data_modeling", "vietnamese_chatbot", "refactored"],
                    importance=0.9,
                    chunk_size=800,
                    overlap_size=100
                )
                
                schemas_chunks = schemas_source.add()
                knowledge_sources["schemas"] = {
                    "source": schemas_source,
                    "chunks": len(schemas_chunks)
                }
                logger.info(f"✅ Loaded CubeJS Schemas knowledge: {len(schemas_chunks)} chunks")
            
            if not knowledge_sources:
                logger.warning("⚠️ No CubeJS knowledge files found in knowledge/cubejs directory")
            
        except Exception as e:
            logger.error(f"❌ Error initializing CubeJS knowledge sources: {e}")
            knowledge_sources = {}
        
        return knowledge_sources
    
    def _initialize_agents(self):
        """Initialize all agents with proper Golett integration"""
        try:
            # Generate schema and knowledge context
            schema_context = self._generate_schema_context()
            knowledge_context = self._get_cubejs_knowledge_context("CubeJS query format time dimensions filters")
            
            # Initialize data analyst agent with enhanced Golett integration
            self.data_analyst_agent = VietnameseDataAnalystAgent(
                memory_manager=self.memory_manager,
                context_manager=self.context_manager,
                session_id=self.session_id,
                cubejs_api_url=self.cubejs_api_url,
                cubejs_api_token=self.cubejs_api_token,
                schema_context=schema_context,
                knowledge_context=knowledge_context
            )
            
            # Initialize conversation classifier agent
            self.classifier_agent = VietnameseConversationClassifierAgent(
                memory_manager=self.memory_manager,
                session_id=self.session_id
            )
            
            # Initialize follow-up agent
            self.follow_up_agent = VietnameseFollowUpAgent(
                memory_manager=self.memory_manager,
                context_manager=self.context_manager,
                session_id=self.session_id
            )
            
            # Initialize conversational agent
            self.conversational_agent = VietnameseConversationalAgent(
                memory_manager=self.memory_manager,
                session_id=self.session_id
            )
            
            # Initialize explanation agent
            self.explanation_agent = VietnameseExplanationAgent(
                memory_manager=self.memory_manager,
                context_manager=self.context_manager,
                session_id=self.session_id
            )
            
            logger.info("✅ All Vietnamese BI agents initialized with Golett integration")
            
        except Exception as e:
            logger.error(f"❌ Error initializing agents: {e}")
            raise
    
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

            ❌ DATA NOT AVAILABLE:
            - Supplier information (nhà cung cấp)
            - Delivery performance ratings (đánh giá hiệu suất giao hàng)
            - Individual customer details
            - Product-level inventory
            - Detailed transaction records

            QUERY STRATEGY FOR COMPLEX QUESTIONS:
            - Revenue + Production efficiency → Query sales_metrics THEN production_metrics separately
            - Company performance → Query executive_dashboard OR multiple cubes separately
            - Financial health → Query financial_metrics for detailed data
            - Employee productivity → Query hr_metrics AND production_metrics separately

            CRITICAL RULES:
            1. ONE CUBE PER QUERY - perform multiple queries if you need data from different cubes
            2. ALWAYS use cube prefix (e.g., "sales_metrics.total_revenue", NOT "total_revenue")
            3. Field names are case-sensitive and must match exactly
            4. Use appropriate cube based on question topic
            5. For time dimensions, use "created_at" for most cubes, "report_date" for executive_dashboard
            6. Available time granularities: day, week, month, quarter, year
            7. If asked about unavailable data, explain what IS available and suggest alternatives
        """
    
    def _get_cubejs_knowledge_context(self, query: str) -> str:
        """Retrieve relevant CubeJS knowledge using Golett's knowledge sources"""
        knowledge_context = []
        
        try:
            # Search REST API knowledge
            if "rest_api" in self.knowledge_sources:
                rest_api_source = self.knowledge_sources["rest_api"]["source"]
                rest_api_results = rest_api_source.retrieve(
                    query=query,
                    limit=3,
                    strategy=KnowledgeRetrievalStrategy.HYBRID
                )
                
                for result in rest_api_results:
                    content = result.get("content", result.get("data", ""))
                    if content:
                        knowledge_context.append(f"**CubeJS REST API Knowledge:**\n{content[:500]}...")
            
            # Search schemas knowledge
            if "schemas" in self.knowledge_sources:
                schemas_source = self.knowledge_sources["schemas"]["source"]
                schemas_results = schemas_source.retrieve(
                    query=query,
                    limit=2,
                    strategy=KnowledgeRetrievalStrategy.HYBRID
                )
                
                for result in schemas_results:
                    content = result.get("content", result.get("data", ""))
                    if content:
                        knowledge_context.append(f"**CubeJS Schema Knowledge:**\n{content[:500]}...")
        
        except Exception as e:
            logger.warning(f"Error retrieving CubeJS knowledge: {e}")
        
        return "\n\n".join(knowledge_context) if knowledge_context else ""
    
    def ask(self, question: str) -> str:
        """
        Ask a question with intelligent conversation flow and enhanced Golett memory integration
        
        Args:
            question: Vietnamese business question
            
        Returns:
            Answer with appropriate conversation flow and enhanced Golett context
        """
        try:
            print(f"🤔 Processing question: {question}")
            
            # Store the user message in Golett memory
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="user",
                content=question,
                metadata={
                    "language": "vietnamese",
                    "domain": "business_intelligence",
                    "timestamp": datetime.now().isoformat(),
                    "version": "refactored"
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Step 1: Classify conversation type using dedicated agent
            conversation_type = self._classify_conversation_type(question)
            print(f"🔍 Conversation type detected: {conversation_type}")
            
            # Step 2: Get enhanced context using Golett's core capabilities
            enhanced_context = self._get_enhanced_context(question, conversation_type)
            
            # Step 3: Route to appropriate handler with enhanced context
            answer = self._route_to_handler(question, conversation_type, enhanced_context)
            
            # Step 4: Store response and extract insights
            self._store_response_and_insights(question, answer, conversation_type)
            
            return answer
            
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
                    "version": "refactored"
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            return error_msg
    
    def _classify_conversation_type(self, question: str) -> str:
        """Classify conversation type using dedicated agent"""
        try:
            # Create classification task
            classification_task = self.task_factory.create_classification_task(
                question=question,
                agent=self.classifier_agent.agent
            )
            
            # Execute classification
            classification_crew = Crew(
                agents=[self.classifier_agent.agent],
                tasks=[classification_task],
                verbose=False
            )
            
            result = classification_crew.kickoff()
            classification = str(result).strip().lower()
            
            # Validate result
            valid_types = ["data_analysis", "follow_up", "conversational", "clarification"]
            for valid_type in valid_types:
                if valid_type in classification:
                    return valid_type
            
            # Fallback logic
            return self._fallback_classification(question)
            
        except Exception as e:
            logger.warning(f"Error in conversation classification: {e}")
            return self._fallback_classification(question)
    
    def _fallback_classification(self, question: str) -> str:
        """Fallback classification logic"""
        question_lower = question.lower().strip()
        
        if any(word in question_lower for word in ["bao nhiêu", "số lượng", "doanh thu", "phân tích", "thống kê"]):
            return "data_analysis"
        elif any(word in question_lower for word in ["tại sao", "vì sao", "giải thích", "nghĩa là gì"]):
            return "clarification"
        elif any(word in question_lower for word in ["xin chào", "cảm ơn", "hello", "hi"]):
            return "conversational"
        elif len(question_lower) < 30:
            return "follow_up"
        else:
            return "conversational"
    
    def _get_enhanced_context(self, question: str, conversation_type: str) -> Dict[str, Any]:
        """
        Get enhanced context using Golett's core capabilities with proper memory retrieval
        
        This is the key improvement - proper use of ContextManager with semantic memory lookup!
        """
        try:
            if conversation_type == "data_analysis":
                # For data analysis, get full enhanced context with semantic retrieval
                return self._get_comprehensive_memory_context(question)
            
            elif conversation_type in ["follow_up", "clarification"]:
                # For follow-ups and clarifications, get enhanced context with recent focus
                return self._get_contextual_memory_context(question)
            
            else:
                # For conversational, get basic conversation context with some memory lookup
                return self._get_conversational_memory_context(question)
                
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return {
                "conversation_context": [],
                "bi_context": [],
                "knowledge_context": [],
                "semantic_memories": [],
                "cross_session_insights": []
            }
    
    def _get_comprehensive_memory_context(self, question: str) -> Dict[str, Any]:
        """
        Get comprehensive memory context for data analysis questions
        Uses semantic search across all memory layers
        """
        try:
            # 1. Get enhanced context from data analyst agent (existing BI + knowledge context)
            base_context = self.data_analyst_agent.get_enhanced_context(question)
            
            # 2. Semantic search for relevant memories across all layers
            semantic_memories = self._semantic_memory_search(question, limit=5)
            
            # 3. Get cross-session business insights
            cross_session_insights = self._get_cross_session_insights(question, limit=3)
            
            # 4. Get recent conversation context
            recent_conversation = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=5,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            # 5. Get related conversation summaries
            related_summaries = self._get_related_conversation_summaries(question, limit=3)
            
            return {
                **base_context,  # Include existing BI and knowledge context
                "semantic_memories": semantic_memories,
                "cross_session_insights": cross_session_insights,
                "recent_conversation": recent_conversation,
                "related_summaries": related_summaries
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive memory context: {e}")
            return self.data_analyst_agent.get_enhanced_context(question)
    
    def _get_contextual_memory_context(self, question: str) -> Dict[str, Any]:
        """
        Get contextual memory for follow-up and clarification questions
        Focuses on recent context with some semantic lookup
        """
        try:
            # 1. Get base context
            base_context = self.data_analyst_agent.get_enhanced_context(question)
            
            # 2. Semantic search with focus on recent memories
            semantic_memories = self._semantic_memory_search(
                question, 
                limit=3,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            # 3. Get recent conversation with more detail
            recent_conversation = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=8,  # More context for follow-ups
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            return {
                **base_context,
                "semantic_memories": semantic_memories,
                "recent_conversation": recent_conversation,
                "cross_session_insights": []  # Less cross-session for follow-ups
            }
            
        except Exception as e:
            logger.error(f"Error getting contextual memory context: {e}")
            return self.data_analyst_agent.get_enhanced_context(question)
    
    def _get_conversational_memory_context(self, question: str) -> Dict[str, Any]:
        """
        Get memory context for conversational questions
        Light memory lookup with focus on user preferences and greetings
        """
        try:
            # 1. Get recent conversation
            conversation_context = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=5,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            # 2. Light semantic search for user preferences and past interactions
            user_preferences = self._semantic_memory_search(
                f"user preferences greeting conversation {question}",
                limit=2,
                include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
            )
            
            return {
                "conversation_context": conversation_context,
                "user_preferences": user_preferences,
                "bi_context": [],
                "knowledge_context": [],
                "semantic_memories": []
            }
            
        except Exception as e:
            logger.error(f"Error getting conversational memory context: {e}")
            return {
                "conversation_context": [],
                "user_preferences": [],
                "bi_context": [],
                "knowledge_context": []
            }
    
    def _semantic_memory_search(
        self, 
        query: str, 
        limit: int = 5, 
        include_layers: List[MemoryLayer] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across memory layers using correct MemoryManager methods
        """
        try:
            if include_layers is None:
                include_layers = [MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
            
            # Use the correct method: search_across_all_layers for comprehensive search
            semantic_results = self.memory_manager.search_across_all_layers(
                query=query,
                session_id=self.session_id,
                limit=limit,
                include_layer_weights=True
            )
            
            # Filter and format results
            formatted_results = []
            for result in semantic_results:
                formatted_result = {
                    "content": result.get("data", ""),
                    "metadata": result.get("metadata", {}),
                    "similarity_score": result.get("score", 0.0),
                    "weighted_score": result.get("weighted_score", result.get("score", 0.0)),
                    "memory_layer": result.get("metadata", {}).get("searched_in_layer", "unknown"),
                    "timestamp": result.get("metadata", {}).get("timestamp", ""),
                    "context_type": result.get("metadata", {}).get("type", "general")
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} semantic memories for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.warning(f"Error in semantic memory search: {e}")
            # Fallback to message history search
            try:
                message_results = self.memory_manager.search_message_history(
                    query=query,
                    session_id=self.session_id,
                    limit=limit,
                    semantic=True,
                    include_layers=include_layers
                )
                
                # Format message results
                formatted_results = []
                for result in message_results:
                    formatted_result = {
                        "content": result.get("data", ""),
                        "metadata": result.get("metadata", {}),
                        "similarity_score": result.get("score", 0.0),
                        "memory_layer": result.get("metadata", {}).get("searched_in_layer", "unknown"),
                        "timestamp": result.get("metadata", {}).get("timestamp", ""),
                        "context_type": "message"
                    }
                    formatted_results.append(formatted_result)
                
                logger.info(f"Fallback search found {len(formatted_results)} message memories")
                return formatted_results
                
            except Exception as fallback_error:
                logger.warning(f"Fallback search also failed: {fallback_error}")
                return []
    
    def _get_cross_session_insights(self, question: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get business insights from other sessions that might be relevant
        Uses ContextManager's cross-session capabilities
        """
        try:
            # Use ContextManager to retrieve cross-session BI context
            cross_session_bi = self.context_manager.retrieve_bi_context(
                session_id=self.session_id,
                query=question,
                limit=limit,
                include_layers=[MemoryLayer.LONG_TERM],
                cross_session=True  # This is the key - cross-session access!
            )
            
            # Format for use
            formatted_insights = []
            for insight in cross_session_bi:
                formatted_insight = {
                    "insight": insight.get("data", ""),
                    "source_session": insight.get("metadata", {}).get("session_id", "unknown"),
                    "importance": insight.get("importance", 0.0),
                    "timestamp": insight.get("metadata", {}).get("extracted_at", ""),
                    "question_context": insight.get("metadata", {}).get("question", "")
                }
                formatted_insights.append(formatted_insight)
            
            logger.info(f"Found {len(formatted_insights)} cross-session insights")
            return formatted_insights
            
        except Exception as e:
            logger.warning(f"Error getting cross-session insights: {e}")
            return []
    
    def _get_related_conversation_summaries(self, question: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get related conversation summaries using correct MemoryManager methods
        """
        try:
            # Use ContextManager to retrieve conversation summaries
            summary_results = self.context_manager.retrieve_conversation_summaries(
                session_id=self.session_id,
                query=question,
                limit=limit,
                include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
                cross_session=False  # Start with current session only
            )
            
            # If no results, try cross-session
            if not summary_results:
                summary_results = self.context_manager.retrieve_conversation_summaries(
                    session_id=self.session_id,
                    query=question,
                    limit=limit,
                    include_layers=[MemoryLayer.LONG_TERM],
                    cross_session=True
                )
            
            formatted_summaries = []
            for summary in summary_results:
                formatted_summary = {
                    "summary": summary.get("data", ""),
                    "topics": summary.get("metadata", {}).get("topics", []),
                    "timestamp": summary.get("metadata", {}).get("start_time", ""),
                    "conversation_type": summary.get("metadata", {}).get("conversation_type", "unknown"),
                    "session_id": summary.get("metadata", {}).get("session_id", "unknown")
                }
                formatted_summaries.append(formatted_summary)
            
            logger.info(f"Found {len(formatted_summaries)} related conversation summaries")
            return formatted_summaries
            
        except Exception as e:
            logger.warning(f"Error getting related conversation summaries: {e}")
            # Fallback to general context retrieval
            try:
                fallback_results = self.memory_manager.retrieve_context(
                    session_id=self.session_id,
                    query=f"conversation summary {question}",
                    context_types=["conversation_summary"],
                    limit=limit,
                    include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
                    cross_session=False
                )
                
                formatted_summaries = []
                for summary in fallback_results:
                    formatted_summary = {
                        "summary": summary.get("data", ""),
                        "topics": summary.get("metadata", {}).get("topics", []),
                        "timestamp": summary.get("metadata", {}).get("timestamp", ""),
                        "conversation_type": summary.get("metadata", {}).get("type", "unknown")
                    }
                    formatted_summaries.append(formatted_summary)
                
                return formatted_summaries
                
            except Exception as fallback_error:
                logger.warning(f"Fallback conversation summary retrieval failed: {fallback_error}")
                return []
    
    def _route_to_handler(self, question: str, conversation_type: str, enhanced_context: Dict[str, Any]) -> str:
        """Route to appropriate handler based on conversation type"""
        
        try:
            if conversation_type == "data_analysis":
                return self._handle_data_analysis(question, enhanced_context)
            
            elif conversation_type == "follow_up":
                return self._handle_follow_up(question, enhanced_context)
            
            elif conversation_type == "clarification":
                return self._handle_clarification(question, enhanced_context)
            
            else:  # conversational
                return self._handle_conversational(question, enhanced_context)
                
        except Exception as e:
            logger.error(f"Error in conversation routing: {e}")
            return f"❌ Lỗi khi xử lý câu hỏi: {str(e)}"
    
    def _handle_data_analysis(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Handle data analysis questions with enhanced Golett context"""
        try:
            print("📊 Handling data analysis with enhanced Golett context...")
            
            # Create data analysis task with enhanced context
            task = self.task_factory.create_data_analysis_task(
                question=question,
                agent=self.data_analyst_agent.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute with crew
            crew = Crew(
                agents=[self.data_analyst_agent.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return f"❌ Lỗi khi phân tích dữ liệu: {str(e)}"
    
    def _handle_follow_up(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Handle follow-up questions with enhanced Golett context"""
        try:
            print("🔄 Handling follow-up with enhanced Golett context...")
            
            # Create follow-up task with enhanced context
            task = self.task_factory.create_follow_up_task(
                question=question,
                agent=self.follow_up_agent.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute with crew
            crew = Crew(
                agents=[self.follow_up_agent.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in follow-up handling: {e}")
            return f"❌ Lỗi khi xử lý câu hỏi tiếp theo: {str(e)}"
    
    def _handle_clarification(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Handle clarification questions with enhanced Golett context"""
        try:
            print("❓ Handling clarification with enhanced Golett context...")
            
            # Create explanation task with enhanced context
            task = self.task_factory.create_explanation_task(
                question=question,
                agent=self.explanation_agent.agent,
                enhanced_context=enhanced_context
            )
            
            # Execute with crew
            crew = Crew(
                agents=[self.explanation_agent.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in clarification handling: {e}")
            return f"❌ Lỗi khi giải thích: {str(e)}"
    
    def _handle_conversational(self, question: str, enhanced_context: Dict[str, Any]) -> str:
        """Handle conversational questions"""
        try:
            print("💬 Handling conversational question...")
            
            # Create conversational task with enhanced context
            task = self.task_factory.create_conversational_task(
                question=question,
                agent=self.conversational_agent.agent,
                conversation_context=enhanced_context.get("conversation_context", []),
                enhanced_context=enhanced_context
            )
            
            # Execute with crew
            crew = Crew(
                agents=[self.conversational_agent.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in conversational handling: {e}")
            return f"❌ Lỗi khi trò chuyện: {str(e)}"
    
    def _store_response_and_insights(self, question: str, answer: str, conversation_type: str):
        """Store response and extract insights using Golett's capabilities"""
        try:
            # Store the assistant response
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="assistant",
                content=answer,
                metadata={
                    "language": "vietnamese",
                    "domain": "business_intelligence",
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "conversation_type": conversation_type,
                    "version": "refactored"
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Extract and store business insights (for data analysis)
            if conversation_type == "data_analysis":
                self._extract_and_store_insights(question, answer)
            
            # Store conversation context using ContextManager
            self._store_conversation_context(question, answer, conversation_type)
            
        except Exception as e:
            logger.warning(f"Error storing response and insights: {e}")
    
    def _extract_and_store_insights(self, question: str, answer: str):
        """Extract and store business insights using Golett's ContextManager"""
        try:
            insights = self._extract_insights_from_answer(answer)
            
            if insights:
                for insight in insights:
                    # Use ContextManager to store BI context - key improvement!
                    self.context_manager.store_bi_context(
                        session_id=self.session_id,
                        data_type="business_insight",
                        data=insight,
                        description=f"Business insight from Vietnamese BI analysis",
                        importance=0.8,
                        metadata={
                            "source": "vietnamese_chatbot_refactored",
                            "question": question,
                            "language": "vietnamese",
                            "extracted_at": datetime.now().isoformat(),
                            "version": "refactored"
                        },
                        memory_layer=MemoryLayer.LONG_TERM
                    )
                
                logger.info(f"Stored {len(insights)} business insights using ContextManager")
        
        except Exception as e:
            logger.warning(f"Error extracting and storing insights: {e}")
    
    def _extract_insights_from_answer(self, answer: str) -> List[str]:
        """Extract business insights from the answer"""
        insights = []
        
        insight_patterns = [
            "tăng", "giảm", "cao nhất", "thấp nhất", "xu hướng",
            "hiệu suất", "doanh thu", "chi phí", "lợi nhuận",
            "so với", "tháng trước", "năm trước", "cải thiện"
        ]
        
        sentences = answer.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(pattern in sentence.lower() for pattern in insight_patterns):
                insights.append(sentence)
        
        return insights[:3]
    
    def _store_conversation_context(self, question: str, answer: str, conversation_type: str):
        """Store conversation context using Golett's ContextManager"""
        try:
            question_str = str(question) if question is not None else ""
            answer_str = str(answer) if answer is not None else ""
            summary = f"Q: {question_str[:100]}... A: {answer_str[:200]}..."
            
            # Use ContextManager for conversation summary - key improvement!
            self.context_manager.store_conversation_summary(
                session_id=self.session_id,
                summary=summary,
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                topics=self._extract_topics_from_text(question_str + " " + answer_str),
                metadata={
                    "language": "vietnamese",
                    "domain": "business_intelligence",
                    "chatbot": "vietnamese_cubejs_refactored",
                    "conversation_type": conversation_type,
                    "version": "refactored"
                }
            )
            
        except Exception as e:
            logger.warning(f"Error storing conversation context: {e}")
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text"""
        vietnamese_business_topics = {
            "doanh thu": "revenue",
            "bán hàng": "sales", 
            "tài chính": "finance",
            "sản xuất": "production",
            "nhân sự": "hr",
            "công ty": "company",
            "chi phí": "cost",
            "lợi nhuận": "profit",
            "hiệu suất": "efficiency",
            "khách hàng": "customer"
        }
        
        topics = []
        text_lower = text.lower()
        
        for vietnamese_term, english_topic in vietnamese_business_topics.items():
            if vietnamese_term in text_lower:
                topics.append(english_topic)
        
        return list(set(topics))
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get enhanced memory statistics"""
        try:
            session_info = self.session_manager.get_session_info(self.session_id)
            layer_stats = self.memory_manager.get_layer_statistics()
            history = self.memory_manager.get_session_history(self.session_id, limit=1000)
            
            return {
                "session_info": session_info,
                "layer_statistics": layer_stats,
                "conversation_count": len(history),
                "session_id": self.session_id,
                "memory_backend": "Golett Memory System (Enhanced)",
                "version": "refactored",
                "architecture": "modular",
                "agents_count": 5,
                "knowledge_sources": len(self.knowledge_sources)
            }
            
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
                session_type="vietnamese_bi_refactored",
                preferences={
                    "language": "vietnamese", 
                    "domain": "business_intelligence",
                    "version": "refactored"
                }
            )
            
            logger.info(f"🧹 Session memory cleared, new session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test CubeJS connection and enhanced Golett memory system"""
        try:
            # Test CubeJS schema
            schema = self.schema_mapper.refresh_schema()
            
            if "error" in schema:
                return {
                    "status": "error",
                    "message": f"Không thể kết nối CubeJS: {schema['error']}"
                }
            
            # Test enhanced Golett memory
            test_key = f"test_refactored_{datetime.now().timestamp()}"
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="system",
                content="Refactored connection test",
                metadata={"test": True, "version": "refactored"}
            )
            
            return {
                "status": "success",
                "message": f"✅ Kết nối thành công! CubeJS: {schema['total_cubes']} cubes, Enhanced Golett Memory: Active",
                "cubes": list(schema["cubes"].keys()),
                "last_updated": schema["last_updated"],
                "memory_system": "Enhanced Golett Memory System",
                "session_id": self.session_id,
                "version": "refactored",
                "architecture": "modular",
                "agents": ["DataAnalyst", "Classifier", "FollowUp", "Conversational", "Explanation"],
                "knowledge_sources": list(self.knowledge_sources.keys())
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"❌ Lỗi kết nối: {str(e)}"
            }


def main():
    """Start the interactive refactored Vietnamese chatbot"""
    print("🚀 Starting Refactored Vietnamese Business Intelligence Chatbot...")
    print("🔧 Enhanced with proper Golett core integration and modular architecture")
    
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
        # Initialize refactored chatbot
        chatbot = RefactoredVietnameseCubeJSChatbot(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            cubejs_api_url=cubejs_api_url,
            cubejs_api_token=cubejs_api_token,
            user_id="interactive_user_refactored"
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
        print(f"🤖 Agents: {memory_stats.get('agents_count', 0)}")
        print(f"📚 Knowledge Sources: {memory_stats.get('knowledge_sources', 0)}")
        
        print("\n" + "=" * 70)
        print("💬 Refactored Vietnamese BI Chatbot with Enhanced Golett Integration Ready!")
        print("🔧 Features: Modular Architecture | Enhanced Context | Cross-Session Learning")
        print("Type your questions in Vietnamese or 'exit' to quit")
        print("=" * 70)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\n🤔 Câu hỏi của bạn: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'thoát']:
                    print("\n👋 Cảm ơn bạn đã sử dụng chatbot refactored!")
                    break
                
                if not user_input:
                    continue
                
                # Process the question
                print(f"\n🤖 Đang xử lý với enhanced Golett integration...")
                answer = chatbot.ask(user_input)
                print(f"\n💡 **Trả lời (Enhanced):**\n{answer}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Lỗi: {str(e)}")

    except Exception as e:
        print(f"❌ Error starting refactored chatbot: {str(e)}")

if __name__ == "__main__":
    main()