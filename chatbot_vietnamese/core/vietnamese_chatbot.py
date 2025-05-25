#!/usr/bin/env python3
"""
Vietnamese Business Intelligence Chatbot with Proper Golett Memory Integration
"""

import os
import sys
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, Process

# Proper Golett imports
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.session.session_manager import SessionManager
from golett.memory.contextual.context_manager import ContextManager
from golett.tools.cube.query_tools import BuildCubeQueryTool, ExecuteCubeQueryTool, AnalyzeDataPointTool
from golett.knowledge.sources import GolettAdvancedTextFileKnowledgeSource, KnowledgeRetrievalStrategy
from golett.utils.logger import get_logger

# Local imports
from chatbot_vietnamese.utils.dynamic_schema_mapper import DynamicCubeJSSchemaMapper

logger = get_logger(__name__)

class VietnameseCubeJSChatbot:
    """
    Vietnamese Business Intelligence Chatbot using proper Golett memory architecture
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
        Initialize Vietnamese CubeJS Chatbot with proper Golett memory integration
        
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
        
        # Initialize Golett memory system
        logger.info("🔧 Initializing Golett memory system...")
        self.memory_manager = MemoryManager(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            postgres_base_table="vietnamese_chatbot_memories",
            qdrant_base_collection="vietnamese_chatbot_vectors",
            enable_normalized_layers=True
        )
        
        # Initialize session manager
        self.session_manager = SessionManager(self.memory_manager)
        
        # Initialize context manager  
        self.context_manager = ContextManager(self.memory_manager)
        
        # Create or get session
        if session_id:
            self.session_id = session_id
            # Verify session exists or create it
            session_info = self.session_manager.get_session_info(session_id)
            if not session_info:
                logger.info(f"Creating new session with ID: {session_id}")
                self.session_manager.create_session(
                    user_id=user_id,
                    session_type="vietnamese_bi",
                    metadata={"session_id": session_id}
                )
        else:
            # Create new session
            self.session_id = self.session_manager.create_session(
                user_id=user_id,
                session_type="vietnamese_bi",
                preferences={"language": "vietnamese", "domain": "business_intelligence"}
            )
        
        logger.info(f"✅ Session initialized: {self.session_id}")
        
        # Initialize CubeJS components
        self.schema_mapper = DynamicCubeJSSchemaMapper()
        self.schema_mapper.refresh_schema()
        
        # Initialize knowledge sources
        self.knowledge_sources = self._initialize_knowledge_sources()
        
        # Initialize agents
        self._initialize_agents()
        
        logger.info(f"✅ Vietnamese CubeJS Chatbot initialized with Golett memory system (session: {self.session_id})")
    
    def _initialize_knowledge_sources(self) -> Dict[str, Any]:
        """Initialize CubeJS knowledge sources using Golett's proper knowledge system"""
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
                    collection_name="cubejs_rest_api",
                    memory_layer=MemoryLayer.LONG_TERM,
                    tags=["cubejs", "rest_api", "query_format", "vietnamese_chatbot"],
                    importance=0.9,
                    chunk_size=800,
                    overlap_size=100
                )
                
                # Add the knowledge to memory
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
                    collection_name="cubejs_schemas",
                    memory_layer=MemoryLayer.LONG_TERM,
                    tags=["cubejs", "schemas", "data_modeling", "vietnamese_chatbot"],
                    importance=0.9,
                    chunk_size=800,
                    overlap_size=100
                )
                
                # Add the knowledge to memory
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
        """Initialize CrewAI agents for Vietnamese business intelligence"""
        try:
            # Create the main data analyst agent
            self.agent = self._create_data_analyst_agent()
            self.crew = None  # Will be created dynamically per query
            
            logger.info("✅ Vietnamese BI agents initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing agents: {e}")
            raise
    
    def _create_data_analyst_agent(self) -> Agent:
        """Create the Vietnamese data analyst agent with Golett memory integration"""
        
        # Generate clean schema context
        schema_context = self._generate_schema_context()
        
        # Get general CubeJS knowledge context
        general_knowledge = self._get_cubejs_knowledge_context("CubeJS query format time dimensions filters")
        
        return Agent(
            role="Vietnamese Data Analyst with Golett Memory",
            goal="Answer Vietnamese business questions using CubeJS data with proper Golett memory integration",
            backstory=f"""
        You are a Vietnamese business intelligence analyst with expertise in CubeJS data analysis and Golett memory system.
        
        CRITICAL CAPABILITIES:
        1. 🧠 GOLETT MEMORY: You have access to Golett's three-layer memory system (long-term, short-term, in-session)
        2. 📊 CUBEJS EXPERTISE: You understand CubeJS query format and can build proper queries
        3. 🔍 KNOWLEDGE SOURCES: You have access to CubeJS documentation through Golett knowledge system
        4. 🇻🇳 VIETNAMESE FLUENCY: You respond naturally in Vietnamese for business contexts
        
        AVAILABLE DATA SCHEMA:
        {schema_context}
        
        CUBEJS KNOWLEDGE CONTEXT:
        {general_knowledge}
        
        CRITICAL QUERY FORMAT RULES (MUST FOLLOW):
        1. Time dimensions MUST use "dimension" field: {{"dimension": "cube.field", "granularity": "month"}}
        2. Filters MUST use "member" field: {{"member": "cube.field", "operator": "equals", "values": ["value"]}}
        3. Always use cube prefixes: "cube_name.field_name"
        4. When queries fail, use your knowledge fallback to understand and fix errors
        
        GOLETT MEMORY USAGE:
        - Store important business insights in long-term memory
        - Keep session context in short-term memory
        - Use in-session memory for current conversation flow
        - Reference past conversations and learned patterns
        """,
            verbose=True,
            tools=self._create_tools(),
            allow_delegation=False
        )
    
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
        """
    
    def _get_cubejs_knowledge_context(self, query: str) -> str:
        """Retrieve relevant CubeJS knowledge for the query using Golett knowledge sources"""
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
    
    def _create_tools(self) -> List:
        """Create CubeJS tools with Golett memory manager integration"""
        return [
            BuildCubeQueryTool(
                api_url=self.cubejs_api_url,
                api_token=self.cubejs_api_token,
                memory_manager=self.memory_manager
            ),
            ExecuteCubeQueryTool(
                api_url=self.cubejs_api_url,
                api_token=self.cubejs_api_token,
                memory_manager=self.memory_manager
            ),
            AnalyzeDataPointTool(
                api_url=self.cubejs_api_url,
                api_token=self.cubejs_api_token,
                memory_manager=self.memory_manager
            )
        ]
    
    def ask(self, question: str) -> str:
        """
        Ask a question with intelligent conversation flow and proper Golett memory integration
        
        Args:
            question: Vietnamese business question
            
        Returns:
            Answer with appropriate conversation flow and Golett memory-enhanced context
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
                    "timestamp": datetime.now().isoformat()
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Determine conversation flow type
            conversation_type = self._determine_conversation_type(question)
            print(f"🔍 Conversation type detected: {conversation_type}")
            
            # Get conversation context from Golett memory
            conversation_context = self._get_conversation_context(question)
            
            # Route to appropriate handler based on conversation type
            if conversation_type == "data_analysis":
                answer = self._handle_data_analysis_question(question, conversation_context)
            elif conversation_type == "follow_up":
                answer = self._handle_follow_up_question(question, conversation_context)
            elif conversation_type == "conversational":
                answer = self._handle_conversational_question(question, conversation_context)
            elif conversation_type == "clarification":
                answer = self._handle_clarification_question(question, conversation_context)
            else:
                # Default to conversational for unknown types
                answer = self._handle_conversational_question(question, conversation_context)
            
            # Store the assistant response in Golett memory
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="assistant",
                content=answer,
                metadata={
                    "language": "vietnamese",
                    "domain": "business_intelligence",
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "conversation_type": conversation_type
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            # Extract and store business insights (only for data analysis)
            if conversation_type == "data_analysis":
                self._extract_and_store_insights(question, answer)
            
            # Store conversation context
            self._store_conversation_context(question, answer)
            
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
                    "timestamp": datetime.now().isoformat()
                },
                memory_layer=MemoryLayer.IN_SESSION
            )
            
            return error_msg
    
    def _determine_conversation_type(self, question: str) -> str:
        """
        Use an intelligent agent to determine the type of conversation flow needed
        
        Args:
            question: User's question in Vietnamese
            
        Returns:
            Conversation type: 'data_analysis', 'follow_up', 'conversational', 'clarification'
        """
        try:
            # Get recent conversation context for better classification
            recent_context = self._get_conversation_context(question)
            
            # Create a conversation classifier agent
            classifier_agent = Agent(
                role="Vietnamese Conversation Flow Classifier",
                goal="Classify Vietnamese questions to determine the appropriate conversation flow",
                backstory="""You are an expert Vietnamese language classifier specialized in business intelligence conversations. 
                You excel at understanding the intent behind Vietnamese questions and determining whether they need:
                - Data analysis (requires CubeJS tools)
                - Follow-up responses (building on previous conversation)
                - Conversational responses (greetings, thanks, general chat)
                - Clarification/explanation (asking for understanding)
                
                You understand Vietnamese business terminology and can detect when users are asking for specific data vs general conversation.""",
                verbose=False,  # Keep quiet for classification
                allow_delegation=False,
                tools=[]  # No tools needed for classification
            )
            
            # Create classification task
            classification_task = Task(
                description=f"""
Classify this Vietnamese question to determine the conversation flow type: "{question}"

RECENT CONVERSATION CONTEXT:
{recent_context}

CLASSIFICATION RULES:

1. **data_analysis** - Choose this if the question:
   - Asks for specific numbers, metrics, or statistics (bao nhiêu, số lượng, tổng, trung bình)
   - Requests business data (doanh thu, bán hàng, lợi nhuận, chi phí, khách hàng)
   - Asks for comparisons or trends (so sánh, tăng, giảm, xu hướng)
   - Requests reports or analysis (phân tích, báo cáo, thống kê)
   - Mentions time periods (tháng này, năm trước, quý)
   - Asks about performance metrics (hiệu suất, năng suất)

2. **follow_up** - Choose this if the question:
   - Is short and references previous conversation (còn, thêm, nữa, tiếp)
   - Builds on previous analysis (chi tiết hơn, cụ thể hơn)
   - References previous results (về cái đó, về điều này, về kết quả)
   - Asks for additional related information

3. **clarification** - Choose this if the question:
   - Asks for explanation (tại sao, vì sao, làm thế nào, nghĩa là gì)
   - Requests understanding (giải thích, ý nghĩa, nguyên nhân)
   - Seeks definition or meaning (định nghĩa, có nghĩa)

4. **conversational** - Choose this if the question:
   - Is a greeting (xin chào, chào, hello, hi)
   - Is thanks or acknowledgment (cảm ơn, thank you, ok, được)
   - Asks about capabilities (bạn có thể, giúp tôi, hướng dẫn)
   - Is general chat or very short responses

INSTRUCTIONS:
1. Analyze the question content and intent
2. Consider the conversation context if relevant
3. Choose the MOST APPROPRIATE single classification
4. Respond with ONLY the classification type: data_analysis, follow_up, conversational, or clarification
5. Do NOT provide explanation, just the classification

RESPOND WITH ONLY ONE WORD: data_analysis, follow_up, conversational, or clarification
""",
                agent=classifier_agent,
                expected_output="Single word classification: data_analysis, follow_up, conversational, or clarification"
            )
            
            # Create crew and execute classification
            classification_crew = Crew(
                agents=[classifier_agent],
                tasks=[classification_task],
                verbose=False  # Keep quiet for classification
            )
            
            # Execute classification
            result = classification_crew.kickoff()
            classification = str(result).strip().lower()
            
            # Validate and clean the result
            valid_types = ["data_analysis", "follow_up", "conversational", "clarification"]
            
            # Extract the classification from the result
            for valid_type in valid_types:
                if valid_type in classification:
                    return valid_type
            
            # Default fallback logic if agent classification fails
            question_lower = question.lower().strip()
            
            # Quick fallback checks
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
                
        except Exception as e:
            logger.warning(f"Error in agent-based conversation classification: {e}")
            
            # Fallback to simple keyword detection if agent fails
            question_lower = question.lower().strip()
            
            if any(word in question_lower for word in ["bao nhiêu", "số lượng", "doanh thu", "phân tích", "thống kê", "tổng", "trung bình"]):
                return "data_analysis"
            elif any(word in question_lower for word in ["tại sao", "vì sao", "giải thích", "nghĩa là gì", "làm thế nào"]):
                return "clarification"
            elif any(word in question_lower for word in ["xin chào", "cảm ơn", "hello", "hi", "bạn là ai"]):
                return "conversational"
            elif len(question_lower) < 30:
                return "follow_up"
            else:
                return "conversational"

    def _handle_data_analysis_question(self, question: str, conversation_context: str) -> str:
        """Handle questions that require data analysis with CubeJS tools"""
        try:
            print("📊 Handling data analysis question...")
            
            # Get relevant business intelligence context
            bi_context = self._get_bi_context(question)
            
            # Get relevant CubeJS knowledge for this specific question
            relevant_knowledge = self._get_cubejs_knowledge_context(question)
            
            # Create enhanced task with Golett memory context
            task = self._create_memory_enhanced_task(question, conversation_context, bi_context, relevant_knowledge)
            
            # Create crew and execute
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            # Execute the task
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return f"❌ Lỗi khi phân tích dữ liệu: {str(e)}"

    def _handle_follow_up_question(self, question: str, conversation_context: str) -> str:
        """Handle follow-up questions that build on previous conversation"""
        try:
            print("🔄 Handling follow-up question...")
            
            # Create a simpler conversational agent for follow-ups
            follow_up_agent = Agent(
                role="Vietnamese Business Assistant",
                goal="Answer follow-up questions based on previous conversation context",
                backstory="""You are a helpful Vietnamese business assistant. You excel at understanding 
                follow-up questions and providing relevant answers based on previous conversation context.
                You can reference previous data analysis results and provide additional insights.""",
                verbose=True,
                allow_delegation=False,
                tools=[]  # No tools needed for follow-ups
            )
            
            # Create follow-up task
            task = Task(
                description=f"""
Answer this Vietnamese follow-up question: "{question}"

PREVIOUS CONVERSATION CONTEXT:
{conversation_context}

INSTRUCTIONS:
1. Understand the follow-up question in relation to previous conversation
2. Provide a helpful answer in Vietnamese
3. Reference previous data or analysis if relevant
4. If the follow-up requires new data analysis, suggest asking a more specific question
5. Be conversational and helpful

Answer in Vietnamese.
""",
                agent=follow_up_agent,
                expected_output="A helpful Vietnamese response to the follow-up question"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[follow_up_agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in follow-up handling: {e}")
            return f"❌ Lỗi khi xử lý câu hỏi tiếp theo: {str(e)}"

    def _handle_conversational_question(self, question: str, conversation_context: str) -> str:
        """Handle general conversational questions"""
        try:
            print("💬 Handling conversational question...")
            
            # Create a conversational agent
            conversational_agent = Agent(
                role="Vietnamese Business Chatbot",
                goal="Engage in helpful conversation and provide guidance about business intelligence",
                backstory="""You are a friendly Vietnamese business intelligence chatbot. You help users 
                understand business data analysis, explain concepts, and guide them on how to ask 
                effective questions about their business data.""",
                verbose=True,
                allow_delegation=False,
                tools=[]  # No tools needed for conversation
            )
            
            # Create conversational task
            task = Task(
                description=f"""
Respond to this Vietnamese conversational question: "{question}"

CONVERSATION CONTEXT:
{conversation_context}

INSTRUCTIONS:
1. Be friendly and helpful in Vietnamese
2. If it's a greeting, respond warmly
3. If it's a question about capabilities, explain what you can do
4. If it's a thank you, acknowledge gracefully
5. If it's about business intelligence, provide helpful guidance
6. Encourage users to ask specific business questions for data analysis

CAPABILITIES TO MENTION (if relevant):
- Analyze business data (doanh thu, bán hàng, tài chính, sản xuất, nhân sự)
- Create reports and insights
- Answer questions about trends, comparisons, and performance
- Help with Vietnamese business intelligence queries

Answer in Vietnamese with a friendly, professional tone.
""",
                agent=conversational_agent,
                expected_output="A friendly Vietnamese conversational response"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[conversational_agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in conversational handling: {e}")
            return f"❌ Lỗi khi trò chuyện: {str(e)}"

    def _handle_clarification_question(self, question: str, conversation_context: str) -> str:
        """Handle questions asking for clarification or explanation"""
        try:
            print("❓ Handling clarification question...")
            
            # Create an explanation agent
            explanation_agent = Agent(
                role="Vietnamese Business Analyst Explainer",
                goal="Provide clear explanations and clarifications about business concepts and data",
                backstory="""You are an expert Vietnamese business analyst who excels at explaining 
                complex business concepts, data analysis results, and business intelligence insights 
                in simple, understandable terms.""",
                verbose=True,
                allow_delegation=False,
                tools=[]  # No tools needed for explanations
            )
            
            # Create explanation task
            task = Task(
                description=f"""
Provide a clear explanation for this Vietnamese question: "{question}"

CONVERSATION CONTEXT:
{conversation_context}

INSTRUCTIONS:
1. Understand what the user is asking for clarification about
2. Provide a clear, detailed explanation in Vietnamese
3. Use simple language and examples when possible
4. If it's about previous data analysis, explain the results clearly
5. If it's about business concepts, provide educational content
6. Be thorough but easy to understand

Answer in Vietnamese with clear explanations.
""",
                agent=explanation_agent,
                expected_output="A clear Vietnamese explanation answering the clarification question"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[explanation_agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in clarification handling: {e}")
            return f"❌ Lỗi khi giải thích: {str(e)}"
    
    def _get_conversation_context(self, question: str) -> str:
        """Get conversation context from Golett memory"""
        try:
            # Get recent conversation history
            recent_messages = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=10,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            if not recent_messages:
                return "No previous conversation context."
            
            # Format conversation context
            context_parts = ["RECENT CONVERSATION:"]
            for msg in recent_messages[-5:]:  # Last 5 messages
                role = msg.get("metadata", {}).get("role", "unknown")
                # Safely handle content - ensure it's a string before slicing
                raw_content = msg.get("data", "")
                if raw_content is None:
                    content = ""
                else:
                    content = str(raw_content)[:200]  # Convert to string first, then truncate
                context_parts.append(f"{role.upper()}: {content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"Error getting conversation context: {e}")
            return "Error retrieving conversation context."
    
    def _get_bi_context(self, question: str) -> str:
        """Get relevant business intelligence context from Golett memory"""
        try:
            # Search for relevant BI data and insights
            bi_results = self.context_manager.retrieve_bi_context(
                session_id=self.session_id,
                query=question,
                limit=3,
                include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
                cross_session=True
            )
            
            if not bi_results:
                return "No relevant BI context found."
            
            # Format BI context
            context_parts = ["RELEVANT BUSINESS INTELLIGENCE:"]
            for result in bi_results:
                # Safely handle data - ensure it's a string before slicing
                raw_data = result.get("data", "")
                if raw_data is None:
                    data = ""
                else:
                    data = str(raw_data)[:200]  # Convert to string first, then truncate
                description = result.get("metadata", {}).get("description", "")
                context_parts.append(f"- {description}: {data}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"Error getting BI context: {e}")
            return "Error retrieving BI context."
    
    def _create_memory_enhanced_task(self, question: str, conversation_context: str, bi_context: str, relevant_knowledge: str) -> Task:
        """Create analysis task enhanced with Golett memory context"""
        
        return Task(
            description=f"""
Answer this Vietnamese business question: "{question}"

GOLETT MEMORY CONTEXT:
{conversation_context}

{bi_context}

RELEVANT CUBEJS KNOWLEDGE:
{relevant_knowledge}

CRITICAL CUBEJS QUERY LIMITATIONS & RULES (MUST FOLLOW):

🚨 SINGLE CUBE LIMITATION:
- CubeJS can ONLY query ONE CUBE at a time
- You CANNOT join multiple cubes in a single query
- If you need data from multiple cubes, perform SEPARATE queries for each cube
- Example: To compare revenue + production data, do 2 queries:
  1. Query executive_dashboard for revenue data
  2. Query production_metrics for production data

QUERY FORMAT RULES:
1. Time dimensions MUST use "dimension" field (NOT "member"):
   ✅ CORRECT: {{"dimension": "sales_metrics.created_at", "granularity": "month"}}
   ❌ WRONG: {{"member": "sales_metrics.created_at", "granularity": "month"}}

2. Filters MUST use "member" field (NOT "dimension"):
   ✅ CORRECT: {{"member": "sales_metrics.status", "operator": "equals", "values": ["completed"]}}
   ❌ WRONG: {{"dimension": "sales_metrics.status", "operator": "equals", "values": ["completed"]}}

3. Always use cube prefixes: "cube_name.field_name"
4. Available time granularities: day, week, month, quarter, year
5. Common operators: equals, notEquals, gt, gte, lt, lte, contains

AVAILABLE CUBES (query separately):
- executive_dashboard: Revenue, costs, financial metrics
- production_metrics: Production efficiency, labor data
- financial_metrics: Banking, cash flow, debt ratios
- hr_metrics: Employee data, training
- sales_metrics: Sales performance, customers

INSTRUCTIONS:
1. Identify which cube(s) contain the data you need
2. For EACH cube, use BuildCubeQuery to create a separate query
3. Use ExecuteCubeQuery to get data from each cube separately
4. Use AnalyzeDataPoint to analyze each result
5. Combine insights from multiple cubes in your final answer
6. Consider the Golett memory context when providing your answer
7. Reference previous conversations and BI insights if relevant
8. Provide a comprehensive answer in Vietnamese

EXAMPLE WORKFLOW for multi-cube questions:
1. BuildCubeQuery for cube A → ExecuteCubeQuery → AnalyzeDataPoint
2. BuildCubeQuery for cube B → ExecuteCubeQuery → AnalyzeDataPoint  
3. Combine insights from both analyses in final answer

Remember: ONE CUBE PER QUERY - perform multiple queries if needed!
            """,
            expected_output="Comprehensive Vietnamese answer with data analysis and Golett memory context integration",
            agent=self.agent
        )
    
    def _extract_and_store_insights(self, question: str, answer: str):
        """Extract and store business insights using Golett context manager"""
        try:
            # Extract insights from the answer
            insights = self._extract_insights_from_answer(answer)
            
            if insights:
                # Store insights as BI context in long-term memory
                for insight in insights:
                    self.context_manager.store_bi_context(
                        session_id=self.session_id,
                        data_type="business_insight",
                        data=insight,
                        description=f"Business insight from Vietnamese BI analysis",
                        importance=0.8,
                        metadata={
                            "source": "vietnamese_chatbot",
                            "question": question,
                            "language": "vietnamese",
                            "extracted_at": datetime.now().isoformat()
                        },
                        memory_layer=MemoryLayer.LONG_TERM
                    )
                
                logger.info(f"Stored {len(insights)} business insights in Golett memory")
        
        except Exception as e:
            logger.warning(f"Error extracting and storing insights: {e}")
    
    def _extract_insights_from_answer(self, answer: str) -> List[str]:
        """Extract business insights from the answer"""
        insights = []
        
        # Look for key business metrics and trends
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
        
        return insights[:3]  # Limit to top 3 insights
    
    def _store_conversation_context(self, question: str, answer: str):
        """Store conversation context using Golett context manager"""
        try:
            # Store conversation summary as context - safely handle string slicing
            question_str = str(question) if question is not None else ""
            answer_str = str(answer) if answer is not None else ""
            summary = f"Q: {question_str[:100]}... A: {answer_str[:200]}..."
            
            self.context_manager.store_conversation_summary(
                session_id=self.session_id,
                summary=summary,
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                topics=self._extract_topics_from_text(question_str + " " + answer_str),
                metadata={
                    "language": "vietnamese",
                    "domain": "business_intelligence",
                    "chatbot": "vietnamese_cubejs"
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
        
        return list(set(topics))  # Remove duplicates
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get Golett memory statistics"""
        try:
            # Get session info
            session_info = self.session_manager.get_session_info(self.session_id)
            
            # Get layer statistics
            layer_stats = self.memory_manager.get_layer_statistics()
            
            # Get conversation history count
            history = self.memory_manager.get_session_history(self.session_id, limit=1000)
            
            return {
                "session_info": session_info,
                "layer_statistics": layer_stats,
                "conversation_count": len(history),
                "session_id": self.session_id,
                "memory_backend": "Golett Memory System"
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
            # Close the current session
            self.session_manager.close_session(self.session_id)
            
            # Create a new session
            self.session_id = self.session_manager.create_session(
                user_id=self.user_id,
                session_type="vietnamese_bi",
                preferences={"language": "vietnamese", "domain": "business_intelligence"}
            )
            
            logger.info(f"🧹 Session memory cleared, new session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test CubeJS connection and Golett memory system"""
        try:
            # Test CubeJS schema
            schema = self.schema_mapper.refresh_schema()
            
            if "error" in schema:
                return {
                    "status": "error",
                    "message": f"Không thể kết nối CubeJS: {schema['error']}"
                }
            
            # Test Golett memory
            test_key = f"test_{datetime.now().timestamp()}"
            self.memory_manager.store_message(
                session_id=self.session_id,
                role="system",
                content="Connection test",
                metadata={"test": True}
            )
            
            return {
                "status": "success",
                "message": f"✅ Kết nối thành công! CubeJS: {schema['total_cubes']} cubes, Golett Memory: Active",
                "cubes": list(schema["cubes"].keys()),
                "last_updated": schema["last_updated"],
                "memory_system": "Golett Memory System",
                "session_id": self.session_id
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"❌ Lỗi kết nối: {str(e)}"
            }

def main():
    """Start the interactive Vietnamese chatbot with proper Golett integration"""
    print("🚀 Starting Vietnamese Business Intelligence Chatbot with Golett Memory...")
    
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
        # Initialize chatbot
        chatbot = VietnameseCubeJSChatbot(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            cubejs_api_url=cubejs_api_url,
            cubejs_api_token=cubejs_api_token,
            user_id="interactive_user"
        )
        
        # Test connection
        connection_test = chatbot.test_connection()
        print(f"📡 {connection_test['message']}")
        
        if connection_test["status"] == "error":
            print("❌ Cannot start chat without proper connections")
            return
        
        # Show memory stats
        memory_stats = chatbot.get_memory_stats()
        print(f"🧠 Memory Backend: {memory_stats.get('memory_backend', 'Unknown')}")
        print(f"📱 Session ID: {chatbot.session_id}")
        
        print("\n" + "=" * 60)
        print("💬 Vietnamese BI Chatbot with Golett Memory Ready!")
        print("Type your questions in Vietnamese or 'exit' to quit")
        print("=" * 60)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\n🤔 Câu hỏi của bạn: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'thoát']:
                    print("\n👋 Cảm ơn bạn đã sử dụng chatbot!")
                    break
                
                if not user_input:
                    continue
                
                # Process the question
                print(f"\n🤖 Đang xử lý...")
                answer = chatbot.ask(user_input)
                print(f"\n💡 **Trả lời:**\n{answer}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Lỗi: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error starting chatbot: {str(e)}")

if __name__ == "__main__":
    main() 