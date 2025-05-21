from typing import Any, Dict, List, Optional, Tuple, Callable

from crewai import Agent, Crew, Task, Process
from crewai.agent import Agent as CrewAgent

from golett.chat.session import ChatSession
from golett.agents.bi.analyzer import BiQueryAnalyzer
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class ChatFlowManager:
    """
    Manages the conversation flow and decision-making process.
    
    This class orchestrates the interaction between different agents
    to analyze queries, make decisions, and generate appropriate responses.
    """
    
    def __init__(
        self,
        session: ChatSession,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
        temperature: float = 0.7
    ) -> None:
        """
        Initialize the chat flow manager.
        
        Args:
            session: The chat session to manage
            llm_provider: The LLM provider (e.g., "openai", "anthropic")
            llm_model: The LLM model to use
            temperature: The temperature for LLM responses
        """
        self.session = session
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature
        
        # Initialize agents for different stages of the flow
        self._initialize_agents()
        
        logger.info(f"Chat flow manager initialized for session: {session.session_id}")
    
    def _initialize_agents(self) -> None:
        """Initialize the specialized agents for different aspects of the conversation."""
        # Agent for analyzing BI queries and determining if data is needed
        self.query_analyzer = self._create_agent(
            name="BI Query Analyzer",
            role="Business Intelligence Query Analyzer",
            goal="Analyze user queries to determine if they require BI data",
            backstory="""You are a specialized BI query analyzer. Your job is to determine 
                        if a user's query is related to business intelligence data and requires 
                        accessing specific data for a complete response."""
        )
        
        # Agent for determining response strategy
        self.strategy_agent = self._create_agent(
            name="Response Strategist",
            role="Conversation Strategy Expert",
            goal="Determine the optimal response strategy and format",
            backstory="""You are an expert in communication strategy. Your job is to 
                        analyze the conversation context and determine the most effective 
                        way to structure and present the response."""
        )
        
        # Agent for generating the final response
        self.response_agent = self._create_agent(
            name="Response Generator",
            role="AI Assistant Response Generator",
            goal="Generate clear, concise, and helpful responses",
            backstory="""You are an expert in generating responses that communicate 
                        complex information clearly. You can adapt your tone and style 
                        based on the needs of the conversation."""
        )
    
    def _create_agent(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str
    ) -> CrewAgent:
        """
        Create a CrewAI agent with specified parameters.
        
        Args:
            name: Name of the agent
            role: Role of the agent
            goal: Goal of the agent
            backstory: Backstory for the agent
            
        Returns:
            A configured agent
        """
        return Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            llm_model=self.llm_model,
            memory=False  # We handle memory externally
        )
    
    def process_user_message(self, message: str) -> str:
        """
        Process a user message through the full decision flow.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response
        """
        # Store the user message
        self.session.add_user_message(message)
        
        # Step 1: Analyze if the message needs BI data
        should_use_data, data_reasoning = self._analyze_data_needs(message)
        
        # Store the decision
        self.session.store_bi_decision(
            should_use_data=should_use_data,
            reasoning=data_reasoning
        )
        
        # Step 2: Determine appropriate response mode
        response_mode, mode_reasoning = self._determine_response_mode(
            message=message,
            should_use_data=should_use_data
        )
        
        # Store the decision
        self.session.store_response_mode_decision(
            response_mode=response_mode,
            reasoning=mode_reasoning
        )
        
        # Step 3: Generate the response
        response = self._generate_response(
            message=message,
            should_use_data=should_use_data,
            response_mode=response_mode
        )
        
        # Store the assistant's response
        self.session.add_assistant_message(response)
        
        return response
    
    def _analyze_data_needs(self, message: str) -> Tuple[bool, str]:
        """
        Analyze if the message requires BI data.
        
        Args:
            message: The user's message
            
        Returns:
            A tuple of (should_use_data, reasoning)
        """
        # Get conversation history for context
        history = self.session.get_message_history()
        history_text = self._format_history(history)
        
        # Create a task for the query analyzer
        task = Task(
            description=f"""
            Analyze if the user query requires business intelligence data to answer effectively.
            
            User query: "{message}"
            
            Conversation history:
            {history_text}
            
            Determine if this query:
            1. Is asking for business metrics or insights
            2. Requires specific data to answer accurately
            3. References previous data points that should be referenced
            
            Respond with a clear YES or NO decision, followed by your reasoning.
            """,
            agent=self.query_analyzer,
            expected_output="A decision (YES/NO) followed by reasoning"
        )
        
        # Execute the task
        result = task.execute()
        
        # Parse the result
        should_use_data = "yes" in result.lower().split("\n")[0].lower()
        reasoning = "\n".join(result.split("\n")[1:]) if "\n" in result else "No specific reasoning provided."
        
        logger.info(f"Data needs analysis: Use data? {should_use_data}")
        return should_use_data, reasoning
    
    def _determine_response_mode(
        self, 
        message: str, 
        should_use_data: bool
    ) -> Tuple[str, str]:
        """
        Determine the appropriate response mode.
        
        Args:
            message: The user's message
            should_use_data: Whether to use BI data
            
        Returns:
            A tuple of (response_mode, reasoning)
        """
        # Get conversation history for context
        history = self.session.get_message_history()
        history_text = self._format_history(history)
        
        # Create a task for the strategy agent
        task = Task(
            description=f"""
            Determine the most effective response mode for the user query.
            
            User query: "{message}"
            
            Conversation history:
            {history_text}
            
            Data usage decision: {"Will use BI data" if should_use_data else "Will not use BI data"}
            
            Choose one of the following response modes:
            - ANALYTICAL: Structured, data-focused response with clear sections
            - NARRATIVE: Story-based response that weaves data into a narrative
            - CONVERSATIONAL: Friendly, direct response in a casual tone
            - INSTRUCTIONAL: Step-by-step guidance or explanation
            
            Respond with the chosen mode (one word) followed by your reasoning.
            """,
            agent=self.strategy_agent,
            expected_output="A response mode and reasoning"
        )
        
        # Execute the task
        result = task.execute()
        
        # Parse the result
        mode_line = result.split("\n")[0].upper()
        for mode in ["ANALYTICAL", "NARRATIVE", "CONVERSATIONAL", "INSTRUCTIONAL"]:
            if mode in mode_line:
                response_mode = mode.lower()
                break
        else:
            # Default if we couldn't parse
            response_mode = "conversational"
        
        reasoning = "\n".join(result.split("\n")[1:]) if "\n" in result else "No specific reasoning provided."
        
        logger.info(f"Response mode determination: {response_mode}")
        return response_mode, reasoning
    
    def _generate_response(
        self, 
        message: str, 
        should_use_data: bool,
        response_mode: str
    ) -> str:
        """
        Generate the final response.
        
        Args:
            message: The user's message
            should_use_data: Whether to use BI data
            response_mode: The response mode to use
            
        Returns:
            The generated response
        """
        # Get conversation history for context
        history = self.session.get_message_history()
        history_text = self._format_history(history)
        
        # Retrieve relevant context if using data
        context_items = []
        if should_use_data:
            context_items = self.session.get_context_for_query(
                query=message,
                context_types=["bi_data"]
            )
        
        context_text = self._format_context(context_items)
        
        # Get recent decisions for context
        decisions = self.session.get_recent_decisions(limit=3)
        decisions_text = self._format_decisions(decisions)
        
        # Create a task for the response agent
        task = Task(
            description=f"""
            Generate a response to the user query based on the specified parameters.
            
            User query: "{message}"
            
            Conversation history:
            {history_text}
            
            Response parameters:
            - Data usage: {"Use available BI data" if should_use_data else "No specific BI data needed"}
            - Response mode: {response_mode.upper()}
            
            Recent decisions:
            {decisions_text}
            
            {"Relevant context and data:" if context_items else ""}
            {context_text}
            
            Generate a helpful, clear response following the {response_mode} style.
            """,
            agent=self.response_agent,
            expected_output="A complete response to the user query"
        )
        
        # Execute the task
        result = task.execute()
        
        logger.info(f"Generated response in {response_mode} mode")
        return result
    
    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history into a readable text."""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for item in history:
            role = item.get('data', {}).get('role', 'unknown')
            content = item.get('data', {}).get('content', '')
            formatted.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted)
    
    def _format_context(self, context_items: List[Dict[str, Any]]) -> str:
        """Format context items into a readable text."""
        if not context_items:
            return "No relevant context available."
        
        formatted = []
        for item in context_items:
            data_type = item.get('metadata', {}).get('data_type', 'unknown')
            description = item.get('metadata', {}).get('description', '')
            content = item.get('data', {})
            
            formatted.append(f"TYPE: {data_type}")
            formatted.append(f"DESCRIPTION: {description}")
            formatted.append(f"DATA: {content}")
            formatted.append("---")
        
        return "\n".join(formatted)
    
    def _format_decisions(self, decisions: List[Dict[str, Any]]) -> str:
        """Format decisions into a readable text."""
        if not decisions:
            return "No recent decisions available."
        
        formatted = []
        for item in decisions:
            decision_type = item.get('data', {}).get('decision_type', 'unknown')
            description = item.get('data', {}).get('description', '')
            reasoning = item.get('data', {}).get('reasoning', '')
            
            formatted.append(f"DECISION: {decision_type} - {description}")
            formatted.append(f"REASONING: {reasoning}")
            formatted.append("---")
        
        return "\n".join(formatted) 