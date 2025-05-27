"""
Vietnamese Business Intelligence Agents

This module contains agent definitions for the Vietnamese BI chatbot,
properly integrated with Golett's core memory and context management capabilities.
"""

from typing import List, Dict, Any, Optional
from crewai import Agent
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.contextual.context_manager import ContextManager
from golett.tools.cube.query_tools import BuildCubeQueryTool, ExecuteCubeQueryTool, AnalyzeDataPointTool
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class VietnameseDataAnalystAgent:
    """
    Vietnamese Data Analyst Agent with proper Golett memory integration
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        context_manager: ContextManager,
        session_id: str,
        cubejs_api_url: str,
        cubejs_api_token: str = None,
        schema_context: str = "",
        knowledge_context: str = ""
    ):
        """
        Initialize Vietnamese Data Analyst Agent
        
        Args:
            memory_manager: Golett memory manager instance
            context_manager: Golett context manager instance
            session_id: Current session ID
            cubejs_api_url: CubeJS API URL
            cubejs_api_token: CubeJS API token
            schema_context: Available data schema context
            knowledge_context: CubeJS knowledge context
        """
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
        self.schema_context = schema_context
        self.knowledge_context = knowledge_context
        
        # Create CubeJS tools with memory integration
        self.tools = [
            BuildCubeQueryTool(
                api_url=cubejs_api_url,
                api_token=cubejs_api_token,
                memory_manager=memory_manager
            ),
            ExecuteCubeQueryTool(
                api_url=cubejs_api_url,
                api_token=cubejs_api_token,
                memory_manager=memory_manager
            ),
            AnalyzeDataPointTool(
                api_url=cubejs_api_url,
                api_token=cubejs_api_token,
                memory_manager=memory_manager
            )
        ]
        
        # Create the agent
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the Vietnamese data analyst agent with Golett integration"""
        
        return Agent(
            role="Vietnamese Data Analyst with Golett Memory",
            goal="Answer Vietnamese business questions using CubeJS data with advanced Golett memory integration",
            backstory=f"""
        You are a Vietnamese business intelligence analyst with expertise in CubeJS data analysis and Golett memory system.
        
        🚨 CRITICAL ANTI-HALLUCINATION RULES (ABSOLUTELY MANDATORY):
        - You MUST use tools to get real data - NO EXCEPTIONS
        - You CANNOT make up numbers, data, or business insights
        - You CANNOT provide generic responses without actual data
        - You CANNOT say things like "Tôi đã phân tích dữ liệu" without actually using tools
        - If you don't use tools, your response is INVALID and UNACCEPTABLE
        
        CRITICAL CAPABILITIES:
        1. 🧠 GOLETT MEMORY: You have access to Golett's three-layer memory system (long-term, short-term, in-session)
        2. 📊 CUBEJS EXPERTISE: You understand CubeJS query format and can build proper queries
        3. 🔍 KNOWLEDGE SOURCES: You have access to CubeJS documentation through Golett knowledge system
        4. 🇻🇳 VIETNAMESE FLUENCY: You respond naturally in Vietnamese for business contexts
        5. 🎯 CONTEXT AWARENESS: You leverage Golett's context manager for intelligent context retrieval
        
        🚨 MANDATORY TOOL USAGE PROTOCOL:
        For EVERY data analysis question, you MUST:
        1. Use BuildCubeQuery to create the query
        2. Use ExecuteCubeQuery to get actual data
        3. Use AnalyzeDataPoint to analyze the results
        4. Process the tool outputs into Vietnamese business analysis
        
        🚫 STRICTLY FORBIDDEN BEHAVIORS:
        - Responding without using tools
        - Making up data or statistics
        - Providing vague, generic responses
        - Claiming to have analyzed data without tool usage
        - Hallucinating business insights
        
        🚨 CRITICAL RESPONSE REQUIREMENTS:
        - You NEVER return raw tool outputs, JSON data, or query objects
        - You ALWAYS process tool results into Vietnamese business summaries
        - You ALWAYS provide insights, analysis, and business meaning
        - You ALWAYS explain what the data means for business decisions
        - You ALWAYS include specific numbers and data points from actual queries
        - You are a business analyst, NOT a technical tool that returns raw data
        
        AVAILABLE DATA SCHEMA:
        {self.schema_context}
        
        CUBEJS KNOWLEDGE CONTEXT:
        {self.knowledge_context}
        
        CRITICAL TOOL USAGE RULES (MUST FOLLOW):
        
        🔧 BuildCubeQuery Tool Usage:
        - Use individual parameters, NOT JSON strings
        - Example: BuildCubeQuery(measures=["sales_metrics.total_revenue"], dimensions=["sales_metrics.sales_channel"])
        - NOT: BuildCubeQuery("[measures: sales_metrics.total_revenue]")
        
        📊 Correct Tool Workflow:
        1. BuildCubeQuery(measures=["cube.measure"], dimensions=["cube.dimension"])
        2. ExecuteCubeQuery(query=<result_from_step_1>)
        3. AnalyzeDataPoint(query_result=<result_from_step_2>)
        4. **MOST IMPORTANT**: Process all tool outputs into Vietnamese business analysis
        
        🚨 CRITICAL QUERY FORMAT RULES:
        1. Time dimensions MUST use "dimension" field: {{"dimension": "cube.field", "granularity": "month"}}
        2. Filters MUST use "member" field: {{"member": "cube.field", "operator": "equals", "values": ["value"]}}
        3. Always use cube prefixes: "cube_name.field_name"
        4. When queries fail, use your knowledge fallback to understand and fix errors
        
        TOOL PARAMETER EXAMPLES:
        - measures: ["sales_metrics.total_revenue", "sales_metrics.total_orders"]
        - dimensions: ["sales_metrics.sales_channel"]
        - time_dimensions: [{{"dimension": "sales_metrics.created_at", "granularity": "month"}}]
        - filters: [{{"member": "sales_metrics.sales_channel", "operator": "equals", "values": ["online"]}}]
        - limit: 10
        
        VIETNAMESE BUSINESS ANALYSIS FORMAT:
        📊 **Phân tích dữ liệu:** [Vietnamese summary of findings with ACTUAL numbers]
        💡 **Insights kinh doanh:** [Business insights based on REAL data]
        📈 **Khuyến nghị:** [Actionable recommendations based on ACTUAL analysis]
        🔍 **Dữ liệu cụ thể:** [Specific data points and metrics from queries]
        
        GOLETT MEMORY USAGE:
        - Use context_manager to retrieve relevant business intelligence context
        - Store important business insights in long-term memory through memory_manager
        - Leverage cross-session knowledge for better insights
        - Reference past conversations and learned patterns intelligently
        
        VALIDATION BEFORE RESPONDING:
        - Did I use BuildCubeQuery, ExecuteCubeQuery, and AnalyzeDataPoint?
        - Do I have specific numbers and data points in my response?
        - Am I providing insights based on actual data, not generic statements?
        - Would someone reading this know exactly what data I found?
        
        Remember: You are a Vietnamese business analyst who provides insights based on REAL DATA, NOT a tool that returns raw data or makes up information!
        """,
            verbose=True,
            tools=self.tools,
            allow_delegation=False
        )
    
    def get_enhanced_context(self, question: str) -> Dict[str, Any]:
        """
        Get enhanced context using Golett's core capabilities
        
        Args:
            question: User's question
            
        Returns:
            Enhanced context including BI data, knowledge, and conversation history
        """
        try:
            # Use Golett's context manager for intelligent BI context retrieval
            bi_context = self.context_manager.retrieve_bi_context(
                session_id=self.session_id,
                query=question,
                limit=5,
                include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
                cross_session=True
            )
            
            # Get knowledge context for CubeJS-specific queries
            knowledge_context = self.context_manager.retrieve_knowledge_for_query(
                session_id=self.session_id,
                query=question,
                tags=["cubejs", "query_format", "schemas"],
                limit=3,
                include_layers=[MemoryLayer.LONG_TERM],
                cross_session=True
            )
            
            # Get recent conversation context
            conversation_context = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=5,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            return {
                "bi_context": bi_context,
                "knowledge_context": knowledge_context,
                "conversation_context": conversation_context
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return {
                "bi_context": [],
                "knowledge_context": [],
                "conversation_context": []
            }


class VietnameseConversationClassifierAgent:
    """
    Agent for classifying Vietnamese conversation types
    """
    
    def __init__(self, memory_manager: MemoryManager, session_id: str):
        """
        Initialize conversation classifier agent
        
        Args:
            memory_manager: Golett memory manager instance
            session_id: Current session ID
        """
        self.memory_manager = memory_manager
        self.session_id = session_id
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the conversation classifier agent"""
        
        return Agent(
            role="Vietnamese Conversation Flow Classifier",
            goal="Classify Vietnamese questions to determine the appropriate conversation flow",
            backstory="""You are an expert Vietnamese language classifier specialized in business intelligence conversations. 
            You excel at understanding the intent behind Vietnamese questions and determining whether they need:
            - Data analysis (requires CubeJS tools)
            - Follow-up responses (building on previous conversation)
            - Conversational responses (greetings, thanks, general chat)
            - Clarification/explanation (asking for understanding)
            
            You understand Vietnamese business terminology and can detect when users are asking for specific data vs general conversation.
            You have access to Golett memory system to understand conversation context.""",
            verbose=False,
            allow_delegation=False,
            tools=[]
        )


class VietnameseFollowUpAgent:
    """
    Agent for handling follow-up questions
    """
    
    def __init__(self, memory_manager: MemoryManager, context_manager: ContextManager, session_id: str):
        """
        Initialize follow-up agent
        
        Args:
            memory_manager: Golett memory manager instance
            context_manager: Golett context manager instance
            session_id: Current session ID
        """
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the follow-up agent"""
        
        return Agent(
            role="Vietnamese Business Assistant",
            goal="Answer follow-up questions based on previous conversation context using Golett memory",
            backstory="""You are a helpful Vietnamese business assistant with access to Golett's advanced memory system. 
            You excel at understanding follow-up questions and providing relevant answers based on:
            - Previous conversation context from Golett memory
            - Business intelligence insights stored in memory layers
            - Cross-session knowledge when relevant
            
            You can reference previous data analysis results and provide additional insights using Golett's context manager.""",
            verbose=True,
            allow_delegation=False,
            tools=[]
        )


class VietnameseConversationalAgent:
    """
    Agent for general conversational interactions
    """
    
    def __init__(self, memory_manager: MemoryManager, session_id: str):
        """
        Initialize conversational agent
        
        Args:
            memory_manager: Golett memory manager instance
            session_id: Current session ID
        """
        self.memory_manager = memory_manager
        self.session_id = session_id
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the conversational agent"""
        
        return Agent(
            role="Vietnamese Business Chatbot",
            goal="Engage in helpful conversation and provide guidance about business intelligence",
            backstory="""You are a friendly Vietnamese business intelligence chatbot with access to Golett memory system. 
            You help users understand business data analysis, explain concepts, and guide them on how to ask 
            effective questions about their business data.
            
            You can reference past conversations and user preferences stored in Golett memory to provide 
            personalized assistance.""",
            verbose=True,
            allow_delegation=False,
            tools=[]
        )


class VietnameseExplanationAgent:
    """
    Agent for providing explanations and clarifications
    """
    
    def __init__(self, memory_manager: MemoryManager, context_manager: ContextManager, session_id: str):
        """
        Initialize explanation agent
        
        Args:
            memory_manager: Golett memory manager instance
            context_manager: Golett context manager instance
            session_id: Current session ID
        """
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the explanation agent"""
        
        return Agent(
            role="Vietnamese Business Analyst Explainer",
            goal="Provide clear explanations and clarifications about business concepts and data using Golett memory",
            backstory="""You are an expert Vietnamese business analyst who excels at explaining 
            complex business concepts, data analysis results, and business intelligence insights 
            in simple, understandable terms.
            
            You have access to Golett's memory system to:
            - Reference previous explanations and build upon them
            - Access stored business knowledge and insights
            - Provide context-aware explanations based on user's history""",
            verbose=True,
            allow_delegation=False,
            tools=[]
        ) 