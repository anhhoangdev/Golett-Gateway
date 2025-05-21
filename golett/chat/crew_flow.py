from typing import Any, Dict, List, Optional, Tuple, Callable, Union
import json
from datetime import datetime

from crewai import Agent, Task, Crew

from golett.chat.crew_session import CrewChatSession
from golett.chat.flow import ChatFlowManager
from golett.agents.bi.analyzer import BiQueryAnalyzer
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class CrewChatFlowManager(ChatFlowManager):
    """
    Enhanced chat flow manager with CrewAI support.
    
    This class extends the standard ChatFlowManager with the ability
    to use CrewAI agents and crews for complex queries and tasks.
    """
    
    def __init__(
        self,
        session: CrewChatSession,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
        temperature: float = 0.7,
        use_crew_for_complex: bool = True,
        auto_summarize: bool = True,
        messages_per_summary: int = 10
    ):
        """
        Initialize the crew-enabled chat flow manager.
        
        Args:
            session: The crew-enabled chat session to manage
            llm_provider: The LLM provider (e.g., "openai", "anthropic")
            llm_model: The LLM model to use
            temperature: The temperature for LLM responses
            use_crew_for_complex: Whether to automatically use crews for complex queries
            auto_summarize: Whether to automatically create conversation summaries
            messages_per_summary: Number of messages before creating a new summary
        """
        super().__init__(session, llm_provider, llm_model, temperature)
        
        # Ensure we're using a CrewChatSession
        if not isinstance(session, CrewChatSession):
            raise TypeError("CrewChatFlowManager requires a CrewChatSession instance")
            
        self.use_crew_for_complex = use_crew_for_complex
        self.auto_summarize = auto_summarize
        self.messages_per_summary = messages_per_summary
        self.message_counter = 0
        
        # Initialize specific crews based on needs
        self._initialize_crews()
        
        logger.info(f"Crew-enabled chat flow manager initialized for session: {session.session_id}")
    
    def _initialize_crews(self) -> None:
        """Initialize specialized crews for different tasks."""
        # Only initialize if not already done
        if hasattr(self.session, 'crews') and self.session.crews:
            return
            
        # Set up BI analysis crew
        if not self.session.get_crew("bi_analysis"):
            bi_analyst = self._create_agent(
                name="BI Analyst",
                role="Business Intelligence Analyst",
                goal="Extract insights from BI data and provide data-driven recommendations"
            )
            
            data_scientist = self._create_agent(
                name="Data Scientist",
                role="Data Scientist",
                goal="Analyze data patterns and provide statistical insights"
            )
            
            self.session.create_crew(
                crew_id="bi_analysis",
                crew_name="BI Analysis Team",
                agents=[bi_analyst, data_scientist],
                process="sequential"
            )
            
        # Set up knowledge crew if we have knowledge capabilities
        if self.session.has_knowledge and not self.session.get_crew("knowledge_crew"):
            knowledge_expert = self._create_agent(
                name="Knowledge Expert",
                role="Domain Knowledge Expert",
                goal="Retrieve and analyze relevant domain knowledge"
            )
            
            context_analyst = self._create_agent(
                name="Context Analyst",
                role="Conversation Context Specialist",
                goal="Analyze conversation history and provide contextual understanding"
            )
            
            self.session.create_crew(
                crew_id="knowledge_crew",
                crew_name="Knowledge Team",
                agents=[knowledge_expert, context_analyst],
                process="sequential"
            )
            
        # Set up summary crew for conversation summarization
        if self.auto_summarize and not self.session.get_crew("summary_crew"):
            summarizer = self._create_agent(
                name="Conversation Summarizer",
                role="Conversation Summarization Specialist",
                goal="Create concise, informative summaries of conversations"
            )
            
            topic_extractor = self._create_agent(
                name="Topic Extractor",
                role="Topic Identification Specialist",
                goal="Identify and categorize topics discussed in conversations"
            )
            
            self.session.create_crew(
                crew_id="summary_crew",
                crew_name="Summarization Team",
                agents=[summarizer, topic_extractor],
                process="sequential"
            )
    
    def process_user_message(self, message: str) -> str:
        """
        Process a user message with potential crew involvement.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response
        """
        # Store the user message
        self.session.add_user_message(message)
        
        # Increment message counter
        self.message_counter += 1
        
        # Step 1: Analyze if this is a complex query requiring a crew
        if self.use_crew_for_complex:
            is_complex, complexity_reasoning = self._analyze_complexity(message)
            
            # Store the complexity decision
            self.session.memory_manager.store_decision(
                session_id=self.session.session_id,
                decision_type="complexity",
                description=f"Query complexity: {'Complex' if is_complex else 'Simple'}",
                reasoning=complexity_reasoning
            )
            
            if is_complex:
                # Use crew-based processing for complex queries
                response = self._process_with_crew(message)
                
                # Check if we should summarize
                if self.auto_summarize and self.message_counter >= self.messages_per_summary:
                    self._create_conversation_summary()
                
                return response
        
        # Fall back to standard processing for simple queries
        response = super().process_user_message(message)
        
        # Check if we should summarize
        if self.auto_summarize and self.message_counter >= self.messages_per_summary:
            self._create_conversation_summary()
            
        return response
    
    def _analyze_complexity(self, message: str) -> Tuple[bool, str]:
        """
        Analyze if a message requires complex processing with a crew.
        
        Args:
            message: The user's message
            
        Returns:
            A tuple of (is_complex, reasoning)
        """
        # Get conversation history for context
        history = self.session.get_message_history()
        history_text = self._format_history(history)
        
        # Create a task for the complexity analyzer
        task = Task(
            description=f"""
            Analyze if the user query is complex and requires specialized knowledge or multi-step reasoning.
            
            User query: "{message}"
            
            Conversation history:
            {history_text}
            
            Determine if this query:
            1. Requires multi-step reasoning or analysis
            2. Needs specialized domain knowledge
            3. Would benefit from multiple experts collaborating
            4. Involves complex data analysis or comparison
            
            Respond with a clear YES or NO decision, followed by your reasoning.
            """,
            agent=self.query_analyzer,  # Reuse the query analyzer from the parent class
            expected_output="A decision (YES/NO) followed by reasoning"
        )
        
        # Execute the task
        result = task.execute()
        
        # Parse the result
        is_complex = "yes" in result.lower().split("\n")[0].lower()
        reasoning = "\n".join(result.split("\n")[1:]) if "\n" in result else "No specific reasoning provided."
        
        # Store in context manager
        self.session.context_manager.store_crew_context(
            session_id=self.session.session_id,
            crew_id="system",
            context_type="complexity_analysis",
            data={
                "message": message,
                "is_complex": is_complex,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Complexity analysis: Complex? {is_complex}")
        return is_complex, reasoning
    
    def _process_with_crew(self, message: str) -> str:
        """
        Process a complex message using appropriate crews.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response
        """
        # Step 1: Determine which crew to use
        crew_id = self._select_appropriate_crew(message)
        
        # Step 2: Enhance the message with context
        enhanced_task = self._create_enhanced_task(message, crew_id)
        
        # Step 3: Execute with the selected crew
        result = self.session.execute_crew_task(
            crew_id=crew_id,
            task_description=enhanced_task
        )
        
        # Step 4: Process and format the crew result
        response = self._format_crew_response(result)
        
        # Store the assistant's response
        self.session.add_assistant_message(response)
        
        return response
    
    def _select_appropriate_crew(self, message: str) -> str:
        """
        Select the most appropriate crew for a given message.
        
        Args:
            message: The user's message
            
        Returns:
            The selected crew ID
        """
        # For simplicity, use a basic heuristic to select crew
        # In a more sophisticated system, this could use ML or complex rules
        
        # Check if it's likely a BI query
        bi_keywords = ["sales", "revenue", "metrics", "numbers", "dashboard", 
                      "report", "trend", "compare", "data", "analysis"]
                      
        if any(keyword in message.lower() for keyword in bi_keywords):
            return "bi_analysis"
            
        # Default to knowledge crew if available, otherwise bi_analysis
        if self.session.has_knowledge and self.session.get_crew("knowledge_crew"):
            return "knowledge_crew"
        else:
            return "bi_analysis"
    
    def _create_enhanced_task(self, message: str, crew_id: str) -> str:
        """
        Create an enhanced task description with context for the crew.
        
        Args:
            message: The user's message
            crew_id: The selected crew ID
            
        Returns:
            Enhanced task description with context
        """
        # Get conversation history
        history = self.session.get_message_history(limit=10)
        history_text = self._format_history(history)
        
        # Get relevant context
        context_items = []
        
        # Get knowledge context if available
        if self.session.has_knowledge:
            knowledge_results = self.session.knowledge_adapter.retrieve_for_query(
                query=message,
                session_id=self.session.session_id
            )
            context_items.extend(knowledge_results)
            
        # Get relevant conversation summaries
        summaries = self.session.context_manager.retrieve_conversation_summaries(
            session_id=self.session.session_id,
            query=message
        )
        context_items.extend(summaries)
        
        # Get previous crew results that might be relevant
        crew_results = self.session.context_manager.retrieve_crew_context(
            session_id=self.session.session_id,
            context_type="task_result",
            query=message
        )
        context_items.extend(crew_results)
        
        context_text = self._format_context(context_items)
        
        # Create enhanced task based on crew type
        if crew_id == "bi_analysis":
            task = f"""
            Analyze and respond to the following business intelligence question:
            
            USER QUERY: "{message}"
            
            CONVERSATION HISTORY:
            {history_text}
            
            {f'RELEVANT CONTEXT:\n{context_text}' if context_text else ''}
            
            Please:
            1. Analyze what BI data would be most relevant to answer this query
            2. Determine which metrics, dimensions, or time periods to analyze
            3. Use appropriate BI tools to retrieve and analyze the data
            4. Provide a clear, concise answer with supporting data
            5. Include visualizations or data summaries where appropriate
            
            Your response should be structured, data-driven, and directly address the user's question.
            """
        elif crew_id == "knowledge_crew":
            task = f"""
            Analyze and respond to the following knowledge-intensive question:
            
            USER QUERY: "{message}"
            
            CONVERSATION HISTORY:
            {history_text}
            
            RELEVANT KNOWLEDGE AND CONTEXT:
            {context_text}
            
            Please:
            1. Analyze what domain knowledge is most relevant to this query
            2. Consider the conversation context and history
            3. Provide a comprehensive yet concise answer
            4. Cite relevant sources or documents where appropriate
            
            Your response should be informative, accurate, and directly address the user's question.
            """
        else:
            # Generic enhanced task for other crews
            task = f"""
            Analyze and respond to the following question:
            
            USER QUERY: "{message}"
            
            CONVERSATION HISTORY:
            {history_text}
            
            {f'RELEVANT CONTEXT:\n{context_text}' if context_text else ''}
            
            Please provide a clear, helpful response that directly addresses the user's query.
            """
        
        return task
    
    def _format_crew_response(self, result: Dict[str, Any]) -> str:
        """
        Format the raw crew result into a polished response.
        
        Args:
            result: The raw result from crew execution
            
        Returns:
            Formatted response
        """
        # Extract the crew's result
        raw_response = result.get("result", "")
        
        # For now, just return the raw response
        # In a more sophisticated system, this could post-process or format
        # the response based on preferences or standards
        return raw_response
        
    def _create_conversation_summary(self) -> None:
        """Create a summary of the recent conversation."""
        if "summary_crew" not in self.session.crews:
            logger.warning("Summary crew not available. Skipping summarization.")
            return
            
        # Number of messages to include in the summary
        history = self.session.get_message_history(limit=self.messages_per_summary + 5)
        
        if len(history) < 3:  # Need at least a few messages to summarize
            return
            
        # Find the index to start from (either from the last summary or beginning)
        start_index = 0
        
        # Create the summary task
        history_text = self._format_history(history)
        
        task_description = f"""
        Create a concise summary of the following conversation segment.
        
        CONVERSATION:
        {history_text}
        
        Please:
        1. Summarize the key points of the conversation
        2. Identify the main topics discussed
        3. Extract any important decisions or conclusions reached
        
        Return your answer in JSON format with these fields:
        {{
            "summary": "your concise summary here",
            "topics": ["topic1", "topic2", "etc"],
            "key_points": ["point1", "point2", "etc"]
        }}
        """
        
        # Execute with the summary crew
        try:
            result = self.session.execute_crew_task(
                crew_id="summary_crew",
                task_description=task_description
            )
            
            # Extract summary data
            raw_result = result.get("result", "")
            
            # Try to parse JSON from the result
            try:
                # Find JSON in the response (it might be surrounded by text)
                json_start = raw_result.find("{")
                json_end = raw_result.rfind("}")
                
                if json_start >= 0 and json_end > json_start:
                    json_str = raw_result[json_start:json_end+1]
                    summary_data = json.loads(json_str)
                    
                    # Store the summary
                    summary = summary_data.get("summary", "")
                    topics = summary_data.get("topics", [])
                    
                    if summary and topics:
                        self.session.store_conversation_summary(
                            summary=summary,
                            topics=topics,
                            start_message_index=0,
                            end_message_index=len(history) - 1
                        )
                        
                        # Reset message counter
                        self.message_counter = 0
                        
                        logger.info(f"Created conversation summary with {len(topics)} topics")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from summary crew result")
        except Exception as e:
            logger.error(f"Error creating conversation summary: {e}")
            # Continue without summary - not critical 