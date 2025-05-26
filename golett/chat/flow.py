from typing import Any, Dict, List, Optional, Tuple, Callable, Protocol
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

from crewai import Agent, Crew, Task, Process
from crewai.agent import Agent as CrewAgent

from golett.chat.session import ChatSession
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class FlowStage(Enum):
    """Standard flow stages for chat processing"""
    ANALYSIS = "analysis"
    STRATEGY = "strategy"
    GENERATION = "generation"
    VALIDATION = "validation"


class FlowDecision:
    """Represents a decision made during the flow"""
    def __init__(self, decision_type: str, value: Any, reasoning: str, confidence: float = 1.0):
        self.decision_type = decision_type
        self.value = value
        self.reasoning = reasoning
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()


class FlowAgentConfig:
    """Configuration for a flow agent"""
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        stage: FlowStage,
        tools: List[Any] = None
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.stage = stage
        self.tools = tools or []


class FlowTaskConfig:
    """Configuration for a flow task"""
    def __init__(
        self,
        stage: FlowStage,
        description_template: str,
        expected_output: str,
        decision_parser: Callable[[str], FlowDecision] = None
    ):
        self.stage = stage
        self.description_template = description_template
        self.expected_output = expected_output
        self.decision_parser = decision_parser or self._default_parser
    
    def _default_parser(self, result: str) -> FlowDecision:
        """Default parser that returns the raw result"""
        return FlowDecision("generic", result, "Raw result")


class ChatFlowManagerBase(ABC):
    """
    Abstract base class for chat flow managers.
    
    This provides a configurable framework for managing conversation flows
    across different domains without hardcoding specific logic.
    """
    
    def __init__(
        self,
        session: ChatSession,
        domain: str = "general",
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
        temperature: float = 0.7
    ) -> None:
        """
        Initialize the chat flow manager.
        
        Args:
            session: The chat session to manage
            domain: The domain this flow manager handles
            llm_provider: The LLM provider (e.g., "openai", "anthropic")
            llm_model: The LLM model to use
            temperature: The temperature for LLM responses
        """
        self.session = session
        self.domain = domain
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature
        
        # Flow configuration
        self.agent_configs = {}
        self.task_configs = {}
        self.flow_stages = []
        self.decisions = {}
        
        # Initialize domain-specific configuration
        self._configure_flow()
        
        # Initialize agents based on configuration
        self._initialize_agents()
        
        logger.info(f"Chat flow manager initialized for domain: {domain}, session: {session.session_id}")
    
    @abstractmethod
    def _configure_flow(self) -> None:
        """Configure the flow stages, agents, and tasks for this domain"""
        pass
    
    def add_agent_config(self, config: FlowAgentConfig) -> None:
        """Add an agent configuration to the flow"""
        self.agent_configs[config.stage] = config
        if config.stage not in self.flow_stages:
            self.flow_stages.append(config.stage)
    
    def add_task_config(self, config: FlowTaskConfig) -> None:
        """Add a task configuration to the flow"""
        self.task_configs[config.stage] = config
    
    def _initialize_agents(self) -> None:
        """Initialize agents based on configuration"""
        self.agents = {}
        for stage, config in self.agent_configs.items():
            self.agents[stage] = self._create_agent(config)
    
    def _create_agent(self, config: FlowAgentConfig) -> CrewAgent:
        """Create a CrewAI agent from configuration"""
        return Agent(
            name=config.name,
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            tools=config.tools,
            verbose=True,
            allow_delegation=False,
            llm_model=self.llm_model,
            memory=False  # We handle memory externally
        )
    
    def process_user_message(self, message: str) -> str:
        """
        Process a user message through the configured flow.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response
        """
        # Store the user message
        self.session.add_user_message(message)
        
        # Process through each configured stage
        for stage in self.flow_stages:
            try:
                decision = self._process_stage(stage, message)
                self.decisions[stage] = decision
                
                # Store decision in session
                self._store_decision(stage, decision)
                
            except Exception as e:
                logger.error(f"Error processing stage {stage}: {e}")
                # Continue with fallback decision
                self.decisions[stage] = FlowDecision(
                    stage.value, 
                    self._get_fallback_decision(stage), 
                    f"Fallback due to error: {e}",
                    confidence=0.1
                )
        
        # Generate final response
        response = self._generate_final_response(message)
        
        # Store the assistant's response
        self.session.add_assistant_message(response)
        
        return response
    
    def _process_stage(self, stage: FlowStage, message: str) -> FlowDecision:
        """Process a single stage of the flow"""
        if stage not in self.task_configs or stage not in self.agents:
            raise ValueError(f"Stage {stage} not properly configured")
        
        task_config = self.task_configs[stage]
        agent = self.agents[stage]
        
        # Create task from template
        task_description = self._format_task_description(
            task_config.description_template, 
            message, 
            stage
        )
        
        task = Task(
            description=task_description,
            agent=agent,
            expected_output=task_config.expected_output
        )
        
        # Execute task
        temp_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )
        
        result = temp_crew.kickoff()
        result_text = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        # Parse result into decision
        decision = task_config.decision_parser(result_text)
        decision.decision_type = stage.value
        
        logger.info(f"Stage {stage.value} completed: {decision.value}")
        return decision
    
    def _format_task_description(self, template: str, message: str, stage: FlowStage) -> str:
        """Format task description with context"""
        # Get conversation history
        history = self.session.get_message_history()
        history_text = self._format_history(history)
        
        # Get previous decisions
        previous_decisions = {
            k.value: v for k, v in self.decisions.items() 
            if k != stage
        }
        decisions_text = self._format_decisions_dict(previous_decisions)
        
        # Get domain-specific context
        domain_context = self._get_domain_context(message, stage)
        context_text = self._format_context(domain_context)
        
        # Format template
        return template.format(
            message=message,
            history=history_text,
            decisions=decisions_text,
            context=context_text,
            domain=self.domain
        )
    
    @abstractmethod
    def _get_domain_context(self, message: str, stage: FlowStage) -> List[Dict[str, Any]]:
        """Get domain-specific context for the stage"""
        pass
    
    @abstractmethod
    def _generate_final_response(self, message: str) -> str:
        """Generate the final response based on all decisions"""
        pass
    
    @abstractmethod
    def _get_fallback_decision(self, stage: FlowStage) -> Any:
        """Get fallback decision for a stage when processing fails"""
        pass
    
    def _store_decision(self, stage: FlowStage, decision: FlowDecision) -> None:
        """Store decision in session"""
        try:
            self.session.store_flow_decision(
                stage=stage.value,
                decision_type=decision.decision_type,
                value=decision.value,
                reasoning=decision.reasoning,
                confidence=decision.confidence
            )
        except Exception as e:
            logger.warning(f"Failed to store decision for stage {stage}: {e}")
    
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
    
    def _format_decisions_dict(self, decisions: Dict[str, FlowDecision]) -> str:
        """Format decisions dictionary into readable text"""
        if not decisions:
            return "No previous decisions."
        
        formatted = []
        for stage, decision in decisions.items():
            formatted.append(f"STAGE: {stage}")
            formatted.append(f"DECISION: {decision.value}")
            formatted.append(f"REASONING: {decision.reasoning}")
            formatted.append(f"CONFIDENCE: {decision.confidence}")
            formatted.append("---")
        
        return "\n".join(formatted)
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get summary of the current flow state"""
        return {
            "domain": self.domain,
            "stages": [stage.value for stage in self.flow_stages],
            "decisions": {
                stage.value: {
                    "value": decision.value,
                    "reasoning": decision.reasoning,
                    "confidence": decision.confidence
                }
                for stage, decision in self.decisions.items()
            },
            "session_id": self.session.session_id
        }


class SimpleConversationalFlowManager(ChatFlowManagerBase):
    """
    Simple implementation for general conversational flow.
    
    This provides a basic flow suitable for general conversation
    without domain-specific requirements.
    """
    
    def _configure_flow(self) -> None:
        """Configure a simple conversational flow"""
        
        # Analysis stage - understand the query
        self.add_agent_config(FlowAgentConfig(
            name="Query Analyzer",
            role="Conversation Analyst",
            goal="Understand the user's intent and requirements",
            backstory=f"""You are an expert at understanding user queries in the {self.domain} domain. 
                         Your job is to analyze what the user is asking for and determine the best approach.""",
            stage=FlowStage.ANALYSIS
        ))
        
        self.add_task_config(FlowTaskConfig(
            stage=FlowStage.ANALYSIS,
            description_template="""
            Analyze the user's query to understand their intent and requirements.
            
            User query: "{message}"
            
            Conversation history:
            {history}
            
            Domain context:
            {context}
            
            Determine:
            1. What is the user asking for?
            2. What type of response would be most helpful?
            3. What information or resources are needed?
            
            Respond with your analysis and recommended approach.
            """,
            expected_output="Analysis of user intent and recommended approach",
            decision_parser=self._parse_analysis_decision
        ))
        
        # Generation stage - create the response
        self.add_agent_config(FlowAgentConfig(
            name="Response Generator",
            role="AI Assistant",
            goal="Generate helpful and appropriate responses",
            backstory=f"""You are a helpful AI assistant specializing in {self.domain}. 
                         You provide clear, accurate, and engaging responses based on the analysis.""",
            stage=FlowStage.GENERATION
        ))
        
        self.add_task_config(FlowTaskConfig(
            stage=FlowStage.GENERATION,
            description_template="""
            Generate a helpful response to the user's query based on the analysis.
            
            User query: "{message}"
            
            Analysis results:
            {decisions}
            
            Conversation history:
            {history}
            
            Domain context:
            {context}
            
            Generate a clear, helpful response that addresses the user's needs.
            """,
            expected_output="A complete and helpful response to the user query",
            decision_parser=self._parse_generation_decision
        ))
    
    def _parse_analysis_decision(self, result: str) -> FlowDecision:
        """Parse analysis result into decision"""
        # Simple parsing - in practice this could be more sophisticated
        intent = "general"
        if "data" in result.lower() or "analysis" in result.lower():
            intent = "data_request"
        elif "help" in result.lower() or "how" in result.lower():
            intent = "help_request"
        elif "explain" in result.lower():
            intent = "explanation_request"
        
        return FlowDecision("intent", intent, result)
    
    def _parse_generation_decision(self, result: str) -> FlowDecision:
        """Parse generation result into decision"""
        return FlowDecision("response", result, "Generated response")
    
    def _get_domain_context(self, message: str, stage: FlowStage) -> List[Dict[str, Any]]:
        """Get domain context - override in domain-specific implementations"""
        try:
            # Try to get context from session if available
            if hasattr(self.session, 'get_context_for_query'):
                return self.session.get_context_for_query(
                    query=message,
                    context_types=["general"]
                )
        except:
            pass
        
        return []
    
    def _generate_final_response(self, message: str) -> str:
        """Generate final response from decisions"""
        if FlowStage.GENERATION in self.decisions:
            return self.decisions[FlowStage.GENERATION].value
        else:
            return f"I understand you're asking about: {message}. Let me help you with that."
    
    def _get_fallback_decision(self, stage: FlowStage) -> Any:
        """Get fallback decision for failed stages"""
        fallbacks = {
            FlowStage.ANALYSIS: "general_query",
            FlowStage.GENERATION: "I'm here to help. Could you please rephrase your question?"
        }
        return fallbacks.get(stage, "unknown")


# Backward compatibility - create a simple flow manager by default
class ChatFlowManager(SimpleConversationalFlowManager):
    """
    Default chat flow manager for backward compatibility.
    
    This provides the same interface as the original ChatFlowManager
    but uses the new configurable architecture.
    """
    pass 