# Golett AI - Crew Building and Chat Flow Creation Guide

## Overview

This guide provides comprehensive instructions for building custom crews and creating new chat flows with Golett AI. You'll learn how to leverage the framework's powerful agent coordination system to create specialized teams for complex tasks.

## Table of Contents

1. [Understanding Crews in Golett AI](#understanding-crews-in-golett-ai)
2. [Basic Crew Creation](#basic-crew-creation)
3. [Advanced Agent Design](#advanced-agent-design)
4. [Custom Chat Flow Implementation](#custom-chat-flow-implementation)
5. [Specialized Crew Examples](#specialized-crew-examples)
6. [Integration with Knowledge Systems](#integration-with-knowledge-systems)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Understanding Crews in Golett AI

### What are Crews?

Crews in Golett AI are collections of specialized AI agents that work together to solve complex problems. Built on CrewAI, they enable:

- **Multi-agent collaboration**: Different agents with specialized skills
- **Task decomposition**: Breaking complex problems into manageable parts
- **Context sharing**: Agents can share information and build on each other's work
- **Persistent memory**: Integration with Golett's memory system for long-term learning

### Core Components

```mermaid
graph TB
    subgraph "Crew Architecture"
        CREW[Crew]
        AGENTS[Agents]
        TASKS[Tasks]
        TOOLS[Tools]
        MEMORY[Memory Integration]
    end
    
    CREW --> AGENTS
    CREW --> TASKS
    AGENTS --> TOOLS
    CREW --> MEMORY
```

1. **Agents**: Specialized AI entities with specific roles and capabilities
2. **Tasks**: Specific objectives assigned to agents
3. **Tools**: External capabilities agents can use (APIs, databases, etc.)
4. **Memory**: Persistent storage and retrieval of context and results

---

## Basic Crew Creation

### Step 1: Set Up the Environment

```python
from golett import (
    MemoryManager, 
    CrewChatSession, 
    CrewChatFlowManager,
    GolettKnowledgeAdapter
)
from crewai import Agent, Task, Crew
from typing import List, Dict, Any, Optional

# Initialize memory manager
memory_manager = MemoryManager(
    postgres_connection="postgresql://user:pass@localhost/golett",
    qdrant_url="http://localhost:6333",
    enable_normalized_layers=True
)

# Create a crew-enabled session
session = CrewChatSession(
    memory_manager=memory_manager,
    metadata={"user_id": "user123", "session_type": "custom_crew"}
)
```

### Step 2: Create Your First Agent

```python
def create_research_agent() -> Agent:
    """Create a research specialist agent."""
    return Agent(
        name="Research Specialist",
        role="Market Research Expert",
        goal="Conduct thorough research and gather relevant information",
        backstory="""You are an expert researcher with years of experience in 
                   market analysis, competitive intelligence, and trend identification. 
                   You excel at finding reliable sources and synthesizing complex 
                   information into actionable insights.""",
        verbose=True,
        allow_delegation=False,
        llm_model="gpt-4o",
        memory=False  # Golett handles memory externally
    )
```

### Step 3: Create Your First Crew

```python
def create_research_crew(session: CrewChatSession) -> str:
    """Create a research crew for market analysis."""
    
    # Create specialized agents
    research_agent = create_research_agent()
    
    analysis_agent = Agent(
        name="Data Analyst",
        role="Data Analysis Specialist", 
        goal="Analyze data and extract meaningful insights",
        backstory="""You are a skilled data analyst with expertise in statistical 
                   analysis, pattern recognition, and insight generation. You can 
                   transform raw data into compelling narratives.""",
        verbose=True,
        allow_delegation=False,
        llm_model="gpt-4o"
    )
    
    # Create the crew
    crew = session.create_crew(
        crew_id="research_crew",
        crew_name="Market Research Team",
        agents=[research_agent, analysis_agent],
        process="sequential",  # Agents work one after another
        verbose=True
    )
    
    return "research_crew"
```

### Step 4: Execute Tasks with Your Crew

```python
def execute_research_task(session: CrewChatSession, crew_id: str, topic: str) -> Dict[str, Any]:
    """Execute a research task using the crew."""
    
    task_description = f"""
    Conduct comprehensive research on: {topic}
    
    Research Agent: Please gather information about:
    1. Current market trends and developments
    2. Key players and competitors
    3. Recent news and announcements
    4. Market size and growth projections
    
    Analysis Agent: Based on the research findings:
    1. Identify key patterns and trends
    2. Assess market opportunities and threats
    3. Provide strategic recommendations
    4. Summarize findings in a clear, actionable format
    
    Provide a comprehensive report with your findings and recommendations.
    """
    
    result = session.execute_crew_task(
        crew_id=crew_id,
        task_description=task_description
    )
    
    return result
```

---

## Advanced Agent Design

### Creating Agents with Tools

```python
from crewai.tools import BaseTool
from typing import Type

class WebSearchTool(BaseTool):
    """Custom tool for web searching."""
    name: str = "web_search"
    description: str = "Search the web for current information"
    
    def _run(self, query: str) -> str:
        # Implement web search logic
        # This is a placeholder - integrate with your preferred search API
        return f"Search results for: {query}"

class DatabaseQueryTool(BaseTool):
    """Custom tool for database queries."""
    name: str = "database_query"
    description: str = "Query internal databases for specific information"
    
    def _run(self, query: str) -> str:
        # Implement database query logic
        return f"Database results for: {query}"

def create_enhanced_research_agent() -> Agent:
    """Create a research agent with custom tools."""
    
    tools = [
        WebSearchTool(),
        DatabaseQueryTool()
    ]
    
    return Agent(
        name="Enhanced Research Specialist",
        role="Senior Market Research Expert",
        goal="Conduct comprehensive research using multiple data sources",
        backstory="""You are a senior research expert with access to multiple 
                   data sources including web search and internal databases. 
                   You excel at cross-referencing information and validating 
                   findings across different sources.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        llm_model="gpt-4o"
    )
```

### Specialized Agent Roles

```python
def create_specialized_agents() -> Dict[str, Agent]:
    """Create a collection of specialized agents for different domains."""
    
    agents = {}
    
    # Financial Analysis Agent
    agents["financial_analyst"] = Agent(
        name="Financial Analyst",
        role="Senior Financial Analyst",
        goal="Analyze financial data and provide investment insights",
        backstory="""You are a CFA-certified financial analyst with 15+ years 
                   of experience in equity research, financial modeling, and 
                   investment analysis. You excel at interpreting financial 
                   statements and market data.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Technical Writer Agent
    agents["technical_writer"] = Agent(
        name="Technical Writer",
        role="Senior Technical Documentation Specialist",
        goal="Create clear, comprehensive technical documentation",
        backstory="""You are an expert technical writer with deep knowledge 
                   of software development, API documentation, and user guides. 
                   You excel at making complex technical concepts accessible.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Customer Success Agent
    agents["customer_success"] = Agent(
        name="Customer Success Manager",
        role="Customer Experience Specialist",
        goal="Analyze customer feedback and improve user experience",
        backstory="""You are a customer success expert with extensive experience 
                   in user research, feedback analysis, and product improvement. 
                   You understand how to translate customer needs into actionable insights.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Quality Assurance Agent
    agents["qa_specialist"] = Agent(
        name="QA Specialist",
        role="Quality Assurance Expert",
        goal="Ensure high quality standards and identify potential issues",
        backstory="""You are a meticulous QA professional with expertise in 
                   testing methodologies, quality standards, and risk assessment. 
                   You have an eye for detail and excel at identifying potential problems.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    return agents
```

---

## Custom Chat Flow Implementation

### Creating a Custom Flow Manager

```python
from golett.chat.crew_flow import CrewChatFlowManager
from golett.memory import MemoryLayer

class CustomChatFlowManager(CrewChatFlowManager):
    """Custom chat flow manager with specialized crew routing."""
    
    def __init__(
        self,
        session: CrewChatSession,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
        temperature: float = 0.7,
        custom_crews: Optional[Dict[str, str]] = None
    ):
        super().__init__(session, llm_provider, llm_model, temperature)
        self.custom_crews = custom_crews or {}
        self._initialize_custom_crews()
    
    def _initialize_custom_crews(self) -> None:
        """Initialize custom crews for specialized tasks."""
        
        # Financial Analysis Crew
        if not self.session.get_crew("financial_analysis"):
            financial_analyst = self._create_financial_agent()
            risk_analyst = self._create_risk_agent()
            
            self.session.create_crew(
                crew_id="financial_analysis",
                crew_name="Financial Analysis Team",
                agents=[financial_analyst, risk_analyst],
                process="sequential"
            )
        
        # Content Creation Crew
        if not self.session.get_crew("content_creation"):
            writer = self._create_writer_agent()
            editor = self._create_editor_agent()
            
            self.session.create_crew(
                crew_id="content_creation",
                crew_name="Content Creation Team",
                agents=[writer, editor],
                process="sequential"
            )
        
        # Customer Support Crew
        if not self.session.get_crew("customer_support"):
            support_agent = self._create_support_agent()
            escalation_agent = self._create_escalation_agent()
            
            self.session.create_crew(
                crew_id="customer_support",
                crew_name="Customer Support Team",
                agents=[support_agent, escalation_agent],
                process="hierarchical"  # Escalation-based process
            )
    
    def _create_financial_agent(self) -> Agent:
        """Create a financial analysis agent."""
        return Agent(
            name="Financial Analyst",
            role="Senior Financial Analyst",
            goal="Provide comprehensive financial analysis and insights",
            backstory="""You are a senior financial analyst with expertise in 
                       financial modeling, valuation, and market analysis. You 
                       excel at interpreting complex financial data and providing 
                       actionable investment insights.""",
            verbose=True,
            llm_model=self.llm_model
        )
    
    def _create_risk_agent(self) -> Agent:
        """Create a risk analysis agent."""
        return Agent(
            name="Risk Analyst",
            role="Risk Management Specialist",
            goal="Identify and assess financial and operational risks",
            backstory="""You are a risk management expert with deep knowledge 
                       of financial markets, regulatory requirements, and risk 
                       assessment methodologies. You excel at identifying potential 
                       risks and developing mitigation strategies.""",
            verbose=True,
            llm_model=self.llm_model
        )
    
    def _select_appropriate_crew(self, message: str) -> str:
        """Enhanced crew selection with custom routing logic."""
        
        # Financial keywords
        financial_keywords = [
            "financial", "investment", "portfolio", "risk", "return",
            "valuation", "earnings", "revenue", "profit", "loss",
            "market", "stock", "bond", "asset", "liability"
        ]
        
        # Content keywords
        content_keywords = [
            "write", "content", "article", "blog", "documentation",
            "guide", "tutorial", "copy", "marketing", "communication"
        ]
        
        # Support keywords
        support_keywords = [
            "help", "support", "issue", "problem", "error",
            "troubleshoot", "fix", "resolve", "assistance"
        ]
        
        message_lower = message.lower()
        
        # Check for financial analysis needs
        if any(keyword in message_lower for keyword in financial_keywords):
            return "financial_analysis"
        
        # Check for content creation needs
        elif any(keyword in message_lower for keyword in content_keywords):
            return "content_creation"
        
        # Check for support needs
        elif any(keyword in message_lower for keyword in support_keywords):
            return "customer_support"
        
        # Fall back to parent class logic
        else:
            return super()._select_appropriate_crew(message)
    
    def _create_enhanced_task(self, message: str, crew_id: str) -> str:
        """Create enhanced tasks with crew-specific context."""
        
        base_task = super()._create_enhanced_task(message, crew_id)
        
        # Add crew-specific enhancements
        if crew_id == "financial_analysis":
            return self._enhance_financial_task(base_task, message)
        elif crew_id == "content_creation":
            return self._enhance_content_task(base_task, message)
        elif crew_id == "customer_support":
            return self._enhance_support_task(base_task, message)
        else:
            return base_task
    
    def _enhance_financial_task(self, base_task: str, message: str) -> str:
        """Enhance task for financial analysis crew."""
        
        financial_context = """
        FINANCIAL ANALYSIS GUIDELINES:
        1. Always consider risk-return tradeoffs
        2. Provide quantitative analysis where possible
        3. Consider market conditions and economic factors
        4. Include regulatory and compliance considerations
        5. Suggest specific actionable recommendations
        
        ANALYSIS FRAMEWORK:
        - Current market conditions
        - Historical performance analysis
        - Risk assessment and mitigation
        - Regulatory compliance check
        - Investment recommendations
        """
        
        return f"{base_task}\n\n{financial_context}"
    
    def _enhance_content_task(self, base_task: str, message: str) -> str:
        """Enhance task for content creation crew."""
        
        content_context = """
        CONTENT CREATION GUIDELINES:
        1. Ensure content is engaging and well-structured
        2. Optimize for target audience and purpose
        3. Include SEO considerations where applicable
        4. Maintain consistent brand voice and tone
        5. Provide clear calls-to-action
        
        CONTENT FRAMEWORK:
        - Audience analysis and targeting
        - Content structure and flow
        - Key messaging and value propositions
        - SEO optimization opportunities
        - Distribution and promotion strategy
        """
        
        return f"{base_task}\n\n{content_context}"
    
    def _enhance_support_task(self, base_task: str, message: str) -> str:
        """Enhance task for customer support crew."""
        
        support_context = """
        CUSTOMER SUPPORT GUIDELINES:
        1. Prioritize customer satisfaction and resolution
        2. Provide clear, step-by-step solutions
        3. Escalate complex issues appropriately
        4. Document solutions for future reference
        5. Follow up to ensure resolution
        
        SUPPORT FRAMEWORK:
        - Issue identification and categorization
        - Root cause analysis
        - Solution development and testing
        - Implementation guidance
        - Follow-up and feedback collection
        """
        
        return f"{base_task}\n\n{support_context}"
```

### Implementing Custom Task Routing

```python
class TaskRouter:
    """Advanced task routing system for crew selection."""
    
    def __init__(self, session: CrewChatSession):
        self.session = session
        self.routing_rules = self._initialize_routing_rules()
    
    def _initialize_routing_rules(self) -> Dict[str, Dict]:
        """Initialize routing rules for different task types."""
        return {
            "financial_analysis": {
                "keywords": [
                    "financial", "investment", "portfolio", "risk", "return",
                    "valuation", "earnings", "revenue", "profit", "market"
                ],
                "complexity_threshold": 0.6,
                "required_agents": ["financial_analyst", "risk_analyst"]
            },
            "technical_documentation": {
                "keywords": [
                    "documentation", "technical", "API", "guide", "tutorial",
                    "specification", "architecture", "implementation"
                ],
                "complexity_threshold": 0.5,
                "required_agents": ["technical_writer", "qa_specialist"]
            },
            "market_research": {
                "keywords": [
                    "research", "market", "competitor", "analysis", "trends",
                    "industry", "survey", "study", "insights"
                ],
                "complexity_threshold": 0.7,
                "required_agents": ["research_specialist", "data_analyst"]
            },
            "customer_experience": {
                "keywords": [
                    "customer", "user", "experience", "feedback", "satisfaction",
                    "support", "service", "journey", "persona"
                ],
                "complexity_threshold": 0.4,
                "required_agents": ["customer_success", "ux_specialist"]
            }
        }
    
    def route_task(self, message: str, context: Dict[str, Any] = None) -> str:
        """Route a task to the most appropriate crew."""
        
        # Analyze message content
        message_lower = message.lower()
        scores = {}
        
        for crew_type, rules in self.routing_rules.items():
            # Calculate keyword match score
            keyword_matches = sum(1 for keyword in rules["keywords"] 
                                if keyword in message_lower)
            keyword_score = keyword_matches / len(rules["keywords"])
            
            # Calculate complexity score (placeholder - implement your logic)
            complexity_score = self._calculate_complexity(message)
            
            # Combine scores
            total_score = (keyword_score * 0.7) + (complexity_score * 0.3)
            scores[crew_type] = total_score
        
        # Select crew with highest score above threshold
        best_crew = max(scores.items(), key=lambda x: x[1])
        
        if best_crew[1] > 0.3:  # Minimum threshold
            return best_crew[0]
        else:
            return "general_purpose"  # Default crew
    
    def _calculate_complexity(self, message: str) -> float:
        """Calculate task complexity based on message content."""
        
        complexity_indicators = [
            "analyze", "compare", "evaluate", "assess", "research",
            "investigate", "develop", "create", "design", "implement"
        ]
        
        message_lower = message.lower()
        complexity_count = sum(1 for indicator in complexity_indicators 
                             if indicator in message_lower)
        
        # Normalize to 0-1 scale
        return min(complexity_count / len(complexity_indicators), 1.0)
```

---

## Specialized Crew Examples

### 1. Business Intelligence Crew

```python
def create_bi_analysis_crew(session: CrewChatSession) -> str:
    """Create a specialized BI analysis crew."""
    
    # Data Analyst Agent
    data_analyst = Agent(
        name="Senior Data Analyst",
        role="Business Intelligence Specialist",
        goal="Extract insights from business data and create actionable reports",
        backstory="""You are a senior data analyst with 10+ years of experience 
                   in business intelligence, data visualization, and statistical 
                   analysis. You excel at transforming raw data into compelling 
                   business insights.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Business Strategist Agent
    strategist = Agent(
        name="Business Strategist",
        role="Strategic Business Analyst",
        goal="Translate data insights into strategic business recommendations",
        backstory="""You are a strategic business analyst with extensive experience 
                   in corporate strategy, market analysis, and business development. 
                   You excel at connecting data insights to business outcomes.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Visualization Specialist Agent
    viz_specialist = Agent(
        name="Data Visualization Expert",
        role="Data Visualization Specialist",
        goal="Create compelling visualizations and dashboards",
        backstory="""You are a data visualization expert with deep knowledge of 
                   design principles, user experience, and data storytelling. 
                   You excel at making complex data accessible and engaging.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    crew = session.create_crew(
        crew_id="bi_analysis_advanced",
        crew_name="Advanced BI Analysis Team",
        agents=[data_analyst, strategist, viz_specialist],
        process="sequential"
    )
    
    return "bi_analysis_advanced"

def execute_bi_analysis(session: CrewChatSession, data_query: str) -> Dict[str, Any]:
    """Execute a comprehensive BI analysis."""
    
    task_description = f"""
    Conduct a comprehensive business intelligence analysis for: {data_query}
    
    Data Analyst: Please perform the following:
    1. Identify relevant data sources and metrics
    2. Conduct statistical analysis of the data
    3. Identify trends, patterns, and anomalies
    4. Calculate key performance indicators
    5. Provide data quality assessment
    
    Business Strategist: Based on the data analysis:
    1. Interpret findings in business context
    2. Identify strategic implications and opportunities
    3. Assess competitive positioning
    4. Recommend specific business actions
    5. Prioritize recommendations by impact and feasibility
    
    Visualization Expert: Create visualization recommendations:
    1. Design appropriate charts and graphs for the data
    2. Suggest dashboard layout and structure
    3. Recommend interactive elements and filters
    4. Ensure accessibility and user experience
    5. Provide implementation guidance
    
    Deliver a comprehensive BI report with data insights, strategic recommendations, 
    and visualization specifications.
    """
    
    return session.execute_crew_task(
        crew_id="bi_analysis_advanced",
        task_description=task_description
    )
```

### 2. Content Strategy Crew

```python
def create_content_strategy_crew(session: CrewChatSession) -> str:
    """Create a content strategy and creation crew."""
    
    # Content Strategist
    strategist = Agent(
        name="Content Strategist",
        role="Senior Content Strategy Expert",
        goal="Develop comprehensive content strategies aligned with business goals",
        backstory="""You are a content strategy expert with 12+ years of experience 
                   in content marketing, brand storytelling, and audience development. 
                   You excel at creating content strategies that drive engagement and conversions.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # SEO Specialist
    seo_specialist = Agent(
        name="SEO Specialist",
        role="Search Engine Optimization Expert",
        goal="Optimize content for search engines and organic discovery",
        backstory="""You are an SEO expert with deep knowledge of search algorithms, 
                   keyword research, and technical SEO. You excel at creating content 
                   that ranks well and drives organic traffic.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Content Creator
    creator = Agent(
        name="Content Creator",
        role="Senior Content Writer and Creator",
        goal="Create engaging, high-quality content across multiple formats",
        backstory="""You are a versatile content creator with expertise in writing, 
                   storytelling, and multimedia content production. You excel at 
                   adapting your voice and style to different audiences and platforms.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Performance Analyst
    analyst = Agent(
        name="Content Performance Analyst",
        role="Content Analytics Specialist",
        goal="Measure and optimize content performance",
        backstory="""You are a content analytics expert with deep knowledge of 
                   content metrics, A/B testing, and performance optimization. 
                   You excel at using data to improve content effectiveness.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    crew = session.create_crew(
        crew_id="content_strategy",
        crew_name="Content Strategy Team",
        agents=[strategist, seo_specialist, creator, analyst],
        process="sequential"
    )
    
    return "content_strategy"
```

### 3. Customer Research Crew

```python
def create_customer_research_crew(session: CrewChatSession) -> str:
    """Create a customer research and insights crew."""
    
    # User Researcher
    researcher = Agent(
        name="User Researcher",
        role="Senior User Experience Researcher",
        goal="Conduct comprehensive user research and gather customer insights",
        backstory="""You are a UX researcher with 8+ years of experience in user 
                   interviews, surveys, usability testing, and behavioral analysis. 
                   You excel at understanding user needs and motivations.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Data Scientist
    data_scientist = Agent(
        name="Customer Data Scientist",
        role="Customer Analytics Specialist",
        goal="Analyze customer data and identify behavioral patterns",
        backstory="""You are a data scientist specializing in customer analytics, 
                   segmentation, and predictive modeling. You excel at extracting 
                   insights from customer data and predicting behavior.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    # Customer Success Manager
    csm = Agent(
        name="Customer Success Manager",
        role="Customer Experience Expert",
        goal="Translate research insights into actionable customer success strategies",
        backstory="""You are a customer success expert with extensive experience 
                   in customer journey mapping, retention strategies, and customer 
                   satisfaction improvement. You excel at turning insights into action.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    crew = session.create_crew(
        crew_id="customer_research",
        crew_name="Customer Research Team",
        agents=[researcher, data_scientist, csm],
        process="sequential"
    )
    
    return "customer_research"
```

---

## Integration with Knowledge Systems

### Adding Knowledge Sources to Crews

```python
def create_knowledge_enhanced_crew(
    session: CrewChatSession,
    knowledge_adapter: GolettKnowledgeAdapter
) -> str:
    """Create a crew with enhanced knowledge capabilities."""
    
    # Add knowledge sources
    knowledge_adapter.add_advanced_file_source(
        file_path="knowledge/company_policies.txt",
        collection_name="company_knowledge",
        memory_layer=MemoryLayer.LONG_TERM,
        tags=["policies", "procedures", "guidelines"],
        importance=0.9
    )
    
    knowledge_adapter.add_advanced_file_source(
        file_path="knowledge/technical_documentation.txt",
        collection_name="technical_docs",
        memory_layer=MemoryLayer.LONG_TERM,
        tags=["technical", "documentation", "API"],
        importance=0.8
    )
    
    # Create knowledge-aware agents
    knowledge_agent = Agent(
        name="Knowledge Expert",
        role="Organizational Knowledge Specialist",
        goal="Retrieve and synthesize relevant organizational knowledge",
        backstory="""You are an expert in organizational knowledge management 
                   with deep understanding of company policies, procedures, and 
                   technical documentation. You excel at finding relevant information 
                   and connecting concepts across different knowledge domains.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    synthesis_agent = Agent(
        name="Knowledge Synthesizer",
        role="Information Synthesis Expert",
        goal="Combine multiple knowledge sources into coherent insights",
        backstory="""You are an expert at synthesizing information from multiple 
                   sources, identifying connections and patterns, and creating 
                   comprehensive understanding from fragmented knowledge.""",
        verbose=True,
        llm_model="gpt-4o"
    )
    
    crew = session.create_crew(
        crew_id="knowledge_enhanced",
        crew_name="Knowledge-Enhanced Team",
        agents=[knowledge_agent, synthesis_agent],
        process="sequential"
    )
    
    return "knowledge_enhanced"

def execute_knowledge_task(
    session: CrewChatSession,
    knowledge_adapter: GolettKnowledgeAdapter,
    query: str
) -> Dict[str, Any]:
    """Execute a task that leverages organizational knowledge."""
    
    # Retrieve relevant knowledge
    knowledge_results = knowledge_adapter.retrieve_knowledge(
        query=query,
        limit=10,
        strategy="hybrid"
    )
    
    # Format knowledge for the crew
    knowledge_context = "\n".join([
        f"Source: {result.get('source', 'Unknown')}\n"
        f"Content: {result.get('content', '')}\n"
        f"Relevance: {result.get('score', 0):.2f}\n"
        for result in knowledge_results
    ])
    
    task_description = f"""
    Answer the following query using organizational knowledge: {query}
    
    AVAILABLE KNOWLEDGE:
    {knowledge_context}
    
    Knowledge Expert: Please analyze the available knowledge and:
    1. Identify the most relevant information for the query
    2. Extract key facts and details
    3. Note any gaps or missing information
    4. Assess the reliability and currency of the information
    
    Knowledge Synthesizer: Based on the expert's analysis:
    1. Synthesize the information into a coherent response
    2. Identify connections between different knowledge sources
    3. Provide a comprehensive answer to the query
    4. Highlight any assumptions or limitations
    5. Suggest additional information that might be helpful
    
    Provide a well-structured, comprehensive response that fully addresses the query.
    """
    
    return session.execute_crew_task(
        crew_id="knowledge_enhanced",
        task_description=task_description
    )
```

### Memory-Aware Task Enhancement

```python
class MemoryAwareTaskEnhancer:
    """Enhance tasks with relevant memory context."""
    
    def __init__(self, session: CrewChatSession):
        self.session = session
        self.memory_manager = session.memory_manager
        self.context_manager = session.context_manager
    
    def enhance_task_with_memory(
        self,
        base_task: str,
        query: str,
        memory_layers: List[MemoryLayer] = None
    ) -> str:
        """Enhance a task with relevant memory context."""
        
        if memory_layers is None:
            memory_layers = [MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
        
        # Retrieve relevant context from memory
        context_items = []
        
        # Get conversation history
        history = self.session.get_message_history(limit=10)
        
        # Get relevant decisions
        decisions = self.memory_manager.get_recent_decisions(
            session_id=self.session.session_id,
            limit=5
        )
        
        # Get relevant BI data
        bi_data = self.memory_manager.retrieve_bi_data(
            session_id=self.session.session_id,
            query=query,
            limit=3
        )
        
        # Get conversation summaries
        summaries = self.context_manager.retrieve_conversation_summaries(
            session_id=self.session.session_id,
            query=query,
            limit=3
        )
        
        # Format memory context
        memory_context = self._format_memory_context(
            history, decisions, bi_data, summaries
        )
        
        # Enhance the task
        enhanced_task = f"""
        {base_task}
        
        RELEVANT MEMORY CONTEXT:
        {memory_context}
        
        Please consider this context when completing the task and reference 
        relevant information where appropriate.
        """
        
        return enhanced_task
    
    def _format_memory_context(
        self,
        history: List[Dict],
        decisions: List[Dict],
        bi_data: List[Dict],
        summaries: List[Dict]
    ) -> str:
        """Format memory context for task enhancement."""
        
        context_parts = []
        
        if history:
            context_parts.append("RECENT CONVERSATION:")
            for msg in history[-5:]:  # Last 5 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]  # Truncate
                context_parts.append(f"{role.upper()}: {content}")
        
        if decisions:
            context_parts.append("\nRECENT DECISIONS:")
            for decision in decisions:
                desc = decision.get('description', '')
                reasoning = decision.get('reasoning', '')
                context_parts.append(f"- {desc}: {reasoning}")
        
        if bi_data:
            context_parts.append("\nRELEVANT BI DATA:")
            for data in bi_data:
                data_type = data.get('data_type', 'unknown')
                description = data.get('description', '')
                context_parts.append(f"- {data_type}: {description}")
        
        if summaries:
            context_parts.append("\nCONVERSATION SUMMARIES:")
            for summary in summaries:
                summary_text = summary.get('summary', '')
                topics = summary.get('topics', [])
                context_parts.append(f"- {summary_text} (Topics: {', '.join(topics)})")
        
        return "\n".join(context_parts)
```

---

## Performance Optimization

### Crew Performance Monitoring

```python
import time
from typing import Dict, Any, List
from datetime import datetime

class CrewPerformanceMonitor:
    """Monitor and optimize crew performance."""
    
    def __init__(self, session: CrewChatSession):
        self.session = session
        self.performance_data = {}
    
    def monitor_crew_execution(
        self,
        crew_id: str,
        task_description: str,
        inputs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Monitor crew execution with performance metrics."""
        
        start_time = time.time()
        
        try:
            # Execute the task
            result = self.session.execute_crew_task(
                crew_id=crew_id,
                task_description=task_description,
                inputs=inputs
            )
            
            execution_time = time.time() - start_time
            success = True
            error = None
            
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            error = str(e)
            result = {"error": error}
        
        # Record performance metrics
        performance_metrics = {
            "crew_id": crew_id,
            "execution_time": execution_time,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "task_length": len(task_description),
            "input_size": len(str(inputs)) if inputs else 0
        }
        
        # Store performance data
        if crew_id not in self.performance_data:
            self.performance_data[crew_id] = []
        self.performance_data[crew_id].append(performance_metrics)
        
        # Store in memory for persistence
        self.session.memory_manager.store_context(
            session_id=self.session.session_id,
            context_type="crew_performance",
            data=performance_metrics,
            importance=0.6
        )
        
        # Add performance metrics to result
        result["performance_metrics"] = performance_metrics
        
        return result
    
    def get_crew_performance_stats(self, crew_id: str) -> Dict[str, Any]:
        """Get performance statistics for a crew."""
        
        if crew_id not in self.performance_data:
            return {"error": f"No performance data for crew {crew_id}"}
        
        data = self.performance_data[crew_id]
        
        execution_times = [d["execution_time"] for d in data if d["success"]]
        success_rate = sum(1 for d in data if d["success"]) / len(data)
        
        stats = {
            "crew_id": crew_id,
            "total_executions": len(data),
            "success_rate": success_rate,
            "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "min_execution_time": min(execution_times) if execution_times else 0,
            "max_execution_time": max(execution_times) if execution_times else 0,
            "recent_errors": [d["error"] for d in data[-5:] if not d["success"]]
        }
        
        return stats
    
    def optimize_crew_performance(self, crew_id: str) -> Dict[str, Any]:
        """Provide optimization recommendations for a crew."""
        
        stats = self.get_crew_performance_stats(crew_id)
        
        if "error" in stats:
            return stats
        
        recommendations = []
        
        # Check execution time
        if stats["average_execution_time"] > 30:  # 30 seconds threshold
            recommendations.append({
                "type": "performance",
                "issue": "High execution time",
                "recommendation": "Consider breaking down complex tasks or optimizing agent instructions"
            })
        
        # Check success rate
        if stats["success_rate"] < 0.9:  # 90% threshold
            recommendations.append({
                "type": "reliability",
                "issue": "Low success rate",
                "recommendation": "Review task descriptions and agent capabilities for better alignment"
            })
        
        # Check for recent errors
        if stats["recent_errors"]:
            recommendations.append({
                "type": "error_handling",
                "issue": "Recent errors detected",
                "recommendation": "Review error patterns and improve error handling in task descriptions"
            })
        
        return {
            "crew_id": crew_id,
            "performance_stats": stats,
            "recommendations": recommendations
        }
```

### Efficient Task Batching

```python
class TaskBatcher:
    """Batch and optimize task execution for better performance."""
    
    def __init__(self, session: CrewChatSession):
        self.session = session
        self.task_queue = []
        self.batch_size = 5
        self.batch_timeout = 60  # seconds
    
    def add_task(
        self,
        crew_id: str,
        task_description: str,
        priority: int = 1,
        inputs: Dict[str, Any] = None
    ) -> str:
        """Add a task to the batch queue."""
        
        task_id = f"task_{len(self.task_queue)}_{int(time.time())}"
        
        task = {
            "task_id": task_id,
            "crew_id": crew_id,
            "task_description": task_description,
            "priority": priority,
            "inputs": inputs,
            "created_at": datetime.now()
        }
        
        self.task_queue.append(task)
        
        return task_id
    
    def execute_batch(self) -> List[Dict[str, Any]]:
        """Execute a batch of tasks."""
        
        if not self.task_queue:
            return []
        
        # Sort by priority (higher priority first)
        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        
        # Take up to batch_size tasks
        batch = self.task_queue[:self.batch_size]
        self.task_queue = self.task_queue[self.batch_size:]
        
        results = []
        
        for task in batch:
            try:
                result = self.session.execute_crew_task(
                    crew_id=task["crew_id"],
                    task_description=task["task_description"],
                    inputs=task["inputs"]
                )
                
                result["task_id"] = task["task_id"]
                result["success"] = True
                
            except Exception as e:
                result = {
                    "task_id": task["task_id"],
                    "success": False,
                    "error": str(e)
                }
            
            results.append(result)
        
        return results
    
    def auto_execute_batches(self) -> None:
        """Automatically execute batches when conditions are met."""
        
        while True:
            # Execute if batch is full or timeout reached
            if (len(self.task_queue) >= self.batch_size or 
                (self.task_queue and 
                 (datetime.now() - self.task_queue[0]["created_at"]).seconds > self.batch_timeout)):
                
                results = self.execute_batch()
                
                # Store batch results
                for result in results:
                    self.session.memory_manager.store_context(
                        session_id=self.session.session_id,
                        context_type="batch_result",
                        data=result,
                        importance=0.5
                    )
            
            time.sleep(5)  # Check every 5 seconds
```

---

## Best Practices

### 1. Agent Design Best Practices

```python
def create_well_designed_agent(
    name: str,
    role: str,
    domain_expertise: List[str],
    tools: List[Any] = None
) -> Agent:
    """Create a well-designed agent following best practices."""
    
    # Construct a comprehensive backstory
    expertise_text = ", ".join(domain_expertise)
    
    backstory = f"""You are a highly skilled {role} with deep expertise in {expertise_text}. 
                  You have years of experience in your field and are known for your analytical 
                  thinking, attention to detail, and ability to communicate complex concepts clearly. 
                  You always strive for accuracy and provide well-reasoned recommendations based 
                  on evidence and best practices."""
    
    # Create clear, specific goal
    goal = f"Provide expert {role.lower()} services with focus on {expertise_text}"
    
    return Agent(
        name=name,
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools or [],
        verbose=True,
        allow_delegation=False,
        llm_model="gpt-4o",
        memory=False  # Let Golett handle memory
    )
```

### 2. Task Description Best Practices

```python
def create_effective_task_description(
    objective: str,
    context: str,
    requirements: List[str],
    deliverables: List[str],
    constraints: List[str] = None
) -> str:
    """Create an effective task description following best practices."""
    
    task_parts = [
        f"OBJECTIVE: {objective}",
        f"\nCONTEXT: {context}",
        "\nREQUIREMENTS:"
    ]
    
    for i, req in enumerate(requirements, 1):
        task_parts.append(f"{i}. {req}")
    
    task_parts.append("\nDELIVERABLES:")
    for i, deliverable in enumerate(deliverables, 1):
        task_parts.append(f"{i}. {deliverable}")
    
    if constraints:
        task_parts.append("\nCONSTRAINTS:")
        for i, constraint in enumerate(constraints, 1):
            task_parts.append(f"{i}. {constraint}")
    
    task_parts.append("\nPlease provide a comprehensive response that addresses all requirements and delivers the specified outputs.")
    
    return "\n".join(task_parts)

# Example usage
task_description = create_effective_task_description(
    objective="Analyze customer satisfaction trends for Q3 2024",
    context="The company has been implementing new customer service initiatives and wants to measure their impact",
    requirements=[
        "Analyze customer satisfaction scores from Q3 2024",
        "Compare with previous quarters",
        "Identify key factors affecting satisfaction",
        "Assess impact of new initiatives"
    ],
    deliverables=[
        "Executive summary of findings",
        "Detailed trend analysis with visualizations",
        "Recommendations for improvement",
        "Action plan for Q4 2024"
    ],
    constraints=[
        "Use only data from the past 12 months",
        "Focus on quantitative metrics",
        "Provide actionable recommendations"
    ]
)
```

### 3. Error Handling and Resilience

```python
class ResilientCrewManager:
    """Crew manager with robust error handling and recovery."""
    
    def __init__(self, session: CrewChatSession):
        self.session = session
        self.retry_attempts = 3
        self.retry_delay = 5  # seconds
    
    def execute_with_retry(
        self,
        crew_id: str,
        task_description: str,
        inputs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute crew task with retry logic."""
        
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                result = self.session.execute_crew_task(
                    crew_id=crew_id,
                    task_description=task_description,
                    inputs=inputs
                )
                
                # Validate result
                if self._validate_result(result):
                    return result
                else:
                    raise ValueError("Invalid result format")
                    
            except Exception as e:
                last_error = e
                
                # Log the error
                self.session.memory_manager.store_context(
                    session_id=self.session.session_id,
                    context_type="crew_error",
                    data={
                        "crew_id": crew_id,
                        "attempt": attempt + 1,
                        "error": str(e),
                        "task_description": task_description[:100]
                    },
                    importance=0.7
                )
                
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                    
                    # Modify task for retry
                    task_description = self._modify_task_for_retry(
                        task_description, attempt + 1
                    )
        
        # All retries failed
        return {
            "success": False,
            "error": f"Failed after {self.retry_attempts} attempts: {last_error}",
            "crew_id": crew_id
        }
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate crew execution result."""
        
        required_fields = ["result", "crew_id"]
        
        for field in required_fields:
            if field not in result:
                return False
        
        # Check if result is not empty
        if not result.get("result") or result["result"].strip() == "":
            return False
        
        return True
    
    def _modify_task_for_retry(self, task_description: str, attempt: int) -> str:
        """Modify task description for retry attempts."""
        
        retry_guidance = f"""
        
        RETRY ATTEMPT {attempt}:
        This is a retry attempt. Please ensure your response is:
        1. Complete and comprehensive
        2. Well-structured and clear
        3. Directly addresses all requirements
        4. Provides specific, actionable information
        
        If you encountered issues in previous attempts, please try a different approach.
        """
        
        return task_description + retry_guidance
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Crew Creation Failures

```python
def diagnose_crew_creation_issues(session: CrewChatSession, crew_id: str) -> Dict[str, Any]:
    """Diagnose common crew creation issues."""
    
    issues = []
    
    # Check if crew already exists
    if session.get_crew(crew_id):
        issues.append({
            "type": "duplicate_crew",
            "message": f"Crew '{crew_id}' already exists",
            "solution": "Use a different crew_id or get the existing crew"
        })
    
    # Check session state
    if not hasattr(session, 'crews'):
        issues.append({
            "type": "session_state",
            "message": "Session crews dictionary not initialized",
            "solution": "Ensure CrewChatSession is properly initialized"
        })
    
    # Check memory manager
    if not session.memory_manager:
        issues.append({
            "type": "memory_manager",
            "message": "Memory manager not available",
            "solution": "Initialize session with a valid MemoryManager"
        })
    
    return {
        "crew_id": crew_id,
        "issues": issues,
        "has_issues": len(issues) > 0
    }
```

#### 2. Task Execution Failures

```python
def diagnose_task_execution_issues(
    session: CrewChatSession,
    crew_id: str,
    task_description: str
) -> Dict[str, Any]:
    """Diagnose task execution issues."""
    
    issues = []
    
    # Check if crew exists
    crew = session.get_crew(crew_id)
    if not crew:
        issues.append({
            "type": "crew_not_found",
            "message": f"Crew '{crew_id}' not found",
            "solution": "Create the crew first or check the crew_id"
        })
        return {"issues": issues, "has_issues": True}
    
    # Check if crew has agents
    if not crew.agents:
        issues.append({
            "type": "no_agents",
            "message": "Crew has no agents",
            "solution": "Add agents to the crew"
        })
    
    # Check task description length
    if len(task_description) < 10:
        issues.append({
            "type": "task_too_short",
            "message": "Task description is too short",
            "solution": "Provide a more detailed task description"
        })
    
    if len(task_description) > 10000:
        issues.append({
            "type": "task_too_long",
            "message": "Task description is too long",
            "solution": "Break down the task into smaller parts"
        })
    
    # Check for unclear instructions
    unclear_indicators = ["maybe", "perhaps", "might", "could be"]
    if any(indicator in task_description.lower() for indicator in unclear_indicators):
        issues.append({
            "type": "unclear_instructions",
            "message": "Task description contains unclear language",
            "solution": "Use more specific and direct language"
        })
    
    return {
        "crew_id": crew_id,
        "issues": issues,
        "has_issues": len(issues) > 0
    }
```

#### 3. Performance Issues

```python
def diagnose_performance_issues(
    session: CrewChatSession,
    crew_id: str,
    execution_time: float
) -> Dict[str, Any]:
    """Diagnose performance issues with crew execution."""
    
    issues = []
    recommendations = []
    
    # Check execution time
    if execution_time > 60:  # 1 minute
        issues.append({
            "type": "slow_execution",
            "message": f"Execution took {execution_time:.2f} seconds",
            "severity": "high" if execution_time > 120 else "medium"
        })
        
        recommendations.extend([
            "Break down complex tasks into smaller parts",
            "Optimize agent instructions for clarity",
            "Consider using fewer agents for simple tasks",
            "Review and optimize any custom tools"
        ])
    
    # Check crew size
    crew = session.get_crew(crew_id)
    if crew and len(crew.agents) > 5:
        issues.append({
            "type": "large_crew",
            "message": f"Crew has {len(crew.agents)} agents",
            "severity": "medium"
        })
        
        recommendations.append("Consider reducing the number of agents for better performance")
    
    # Check memory usage
    memory_stats = session.memory_manager.get_layer_statistics()
    total_items = sum(stats.get('total_items', 0) for stats in memory_stats.values())
    
    if total_items > 10000:
        issues.append({
            "type": "high_memory_usage",
            "message": f"Memory contains {total_items} items",
            "severity": "medium"
        })
        
        recommendations.append("Consider running memory cleanup to improve performance")
    
    return {
        "crew_id": crew_id,
        "execution_time": execution_time,
        "issues": issues,
        "recommendations": recommendations,
        "has_issues": len(issues) > 0
    }
```

### Debug Utilities

```python
class CrewDebugger:
    """Debugging utilities for crew development."""
    
    def __init__(self, session: CrewChatSession):
        self.session = session
    
    def debug_crew_state(self, crew_id: str) -> Dict[str, Any]:
        """Get detailed information about a crew's state."""
        
        crew = self.session.get_crew(crew_id)
        
        if not crew:
            return {"error": f"Crew '{crew_id}' not found"}
        
        debug_info = {
            "crew_id": crew_id,
            "agent_count": len(crew.agents),
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.role,
                    "goal": agent.goal,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
                for agent in crew.agents
            ],
            "process": crew.process,
            "verbose": crew.verbose,
            "task_count": len(crew.tasks) if hasattr(crew, 'tasks') else 0
        }
        
        return debug_info
    
    def debug_session_state(self) -> Dict[str, Any]:
        """Get detailed information about the session state."""
        
        return {
            "session_id": self.session.session_id,
            "crew_count": len(self.session.crews),
            "crew_ids": list(self.session.crews.keys()),
            "has_knowledge": self.session.has_knowledge,
            "memory_manager_available": self.session.memory_manager is not None,
            "context_manager_available": hasattr(self.session, 'context_manager'),
            "session_manager_available": hasattr(self.session, 'session_manager')
        }
    
    def test_crew_basic_functionality(self, crew_id: str) -> Dict[str, Any]:
        """Test basic functionality of a crew."""
        
        test_results = {
            "crew_id": crew_id,
            "tests": []
        }
        
        # Test 1: Crew exists
        crew = self.session.get_crew(crew_id)
        test_results["tests"].append({
            "test": "crew_exists",
            "passed": crew is not None,
            "message": "Crew exists" if crew else "Crew not found"
        })
        
        if not crew:
            return test_results
        
        # Test 2: Has agents
        has_agents = len(crew.agents) > 0
        test_results["tests"].append({
            "test": "has_agents",
            "passed": has_agents,
            "message": f"Has {len(crew.agents)} agents" if has_agents else "No agents"
        })
        
        # Test 3: Simple task execution
        if has_agents:
            try:
                result = self.session.execute_crew_task(
                    crew_id=crew_id,
                    task_description="Please respond with 'Test successful' to confirm you are working correctly."
                )
                
                task_successful = "result" in result and "test successful" in result["result"].lower()
                test_results["tests"].append({
                    "test": "simple_task_execution",
                    "passed": task_successful,
                    "message": "Simple task executed successfully" if task_successful else "Task execution failed"
                })
                
            except Exception as e:
                test_results["tests"].append({
                    "test": "simple_task_execution",
                    "passed": False,
                    "message": f"Task execution error: {str(e)}"
                })
        
        # Overall result
        test_results["overall_passed"] = all(test["passed"] for test in test_results["tests"])
        
        return test_results
```

---

## Complete Example: Building a Custom Analytics Crew

Here's a complete example that demonstrates building a sophisticated analytics crew:

```python
#!/usr/bin/env python3
"""
Complete example: Building a custom analytics crew with Golett AI
"""

import os
from typing import Dict, Any, List
from golett import (
    MemoryManager, 
    CrewChatSession, 
    GolettKnowledgeAdapter
)
from golett.memory import MemoryLayer
from crewai import Agent

class AnalyticsCrewBuilder:
    """Builder for creating sophisticated analytics crews."""
    
    def __init__(self):
        # Initialize Golett components
        self.memory_manager = MemoryManager(
            postgres_connection=os.getenv("POSTGRES_CONNECTION"),
            qdrant_url=os.getenv("QDRANT_URL"),
            enable_normalized_layers=True
        )
        
        self.session = CrewChatSession(
            memory_manager=self.memory_manager,
            metadata={"user_id": "analytics_user", "session_type": "analytics"}
        )
        
        self.knowledge_adapter = GolettKnowledgeAdapter(
            memory_manager=self.memory_manager,
            session_id=self.session.session_id,
            enable_advanced_features=True
        )
    
    def create_analytics_crew(self) -> str:
        """Create a comprehensive analytics crew."""
        
        # Data Analyst Agent
        data_analyst = Agent(
            name="Senior Data Analyst",
            role="Data Analysis Expert",
            goal="Perform comprehensive data analysis and extract meaningful insights",
            backstory="""You are a senior data analyst with 10+ years of experience 
                       in statistical analysis, data mining, and business intelligence. 
                       You excel at finding patterns in complex datasets and translating 
                       data into actionable business insights.""",
            verbose=True,
            llm_model="gpt-4o"
        )
        
        # Statistical Modeler Agent
        statistician = Agent(
            name="Statistical Modeler",
            role="Statistical Analysis Specialist",
            goal="Build statistical models and perform advanced analytics",
            backstory="""You are a statistical expert with deep knowledge of 
                       statistical modeling, hypothesis testing, and predictive analytics. 
                       You excel at building robust statistical models and validating 
                       analytical assumptions.""",
            verbose=True,
            llm_model="gpt-4o"
        )
        
        # Business Intelligence Agent
        bi_specialist = Agent(
            name="BI Specialist",
            role="Business Intelligence Expert",
            goal="Translate analytical findings into business recommendations",
            backstory="""You are a business intelligence expert with extensive 
                       experience in translating complex analytical findings into 
                       clear business recommendations. You excel at understanding 
                       business context and strategic implications.""",
            verbose=True,
            llm_model="gpt-4o"
        )
        
        # Visualization Expert Agent
        viz_expert = Agent(
            name="Visualization Expert",
            role="Data Visualization Specialist",
            goal="Create compelling visualizations and dashboards",
            backstory="""You are a data visualization expert with deep knowledge 
                       of design principles, user experience, and data storytelling. 
                       You excel at creating visualizations that communicate insights 
                       effectively to different audiences.""",
            verbose=True,
            llm_model="gpt-4o"
        )
        
        # Create the crew
        crew_id = "advanced_analytics"
        self.session.create_crew(
            crew_id=crew_id,
            crew_name="Advanced Analytics Team",
            agents=[data_analyst, statistician, bi_specialist, viz_expert],
            process="sequential"
        )
        
        return crew_id
    
    def setup_knowledge_base(self):
        """Set up knowledge base for analytics crew."""
        
        # Add analytics methodology knowledge
        self.knowledge_adapter.add_advanced_file_source(
            file_path="knowledge/analytics_methodologies.txt",
            collection_name="analytics_knowledge",
            memory_layer=MemoryLayer.LONG_TERM,
            tags=["analytics", "methodology", "best_practices"],
            importance=0.9
        )
        
        # Add business context knowledge
        self.knowledge_adapter.add_advanced_file_source(
            file_path="knowledge/business_context.txt",
            collection_name="business_knowledge",
            memory_layer=MemoryLayer.LONG_TERM,
            tags=["business", "context", "domain"],
            importance=0.8
        )
    
    def execute_comprehensive_analysis(
        self,
        analysis_request: str,
        data_description: str = None
    ) -> Dict[str, Any]:
        """Execute a comprehensive analytics workflow."""
        
        # Retrieve relevant knowledge
        knowledge_results = self.knowledge_adapter.retrieve_knowledge(
            query=analysis_request,
            limit=5,
            strategy="hybrid"
        )
        
        # Format knowledge context
        knowledge_context = "\n".join([
            f"- {result.get('content', '')[:200]}..."
            for result in knowledge_results
        ])
        
        # Create comprehensive task description
        task_description = f"""
        COMPREHENSIVE ANALYTICS REQUEST: {analysis_request}
        
        {f'DATA DESCRIPTION: {data_description}' if data_description else ''}
        
        RELEVANT KNOWLEDGE:
        {knowledge_context}
        
        WORKFLOW INSTRUCTIONS:
        
        Data Analyst: Please perform the following analysis:
        1. Understand the business question and data requirements
        2. Identify appropriate analytical approaches and methodologies
        3. Perform exploratory data analysis to understand data characteristics
        4. Identify patterns, trends, and anomalies in the data
        5. Calculate relevant descriptive statistics and metrics
        6. Document data quality issues and limitations
        
        Statistical Modeler: Based on the data analysis:
        1. Determine appropriate statistical methods and models
        2. Validate statistical assumptions and requirements
        3. Build and validate statistical models as appropriate
        4. Perform hypothesis testing where relevant
        5. Assess model performance and statistical significance
        6. Provide confidence intervals and uncertainty estimates
        
        BI Specialist: Translate the analytical findings:
        1. Interpret statistical results in business context
        2. Identify key business insights and implications
        3. Assess strategic and operational impacts
        4. Develop specific, actionable recommendations
        5. Prioritize recommendations by impact and feasibility
        6. Consider implementation challenges and requirements
        
        Visualization Expert: Create visualization recommendations:
        1. Design appropriate charts and visualizations for the findings
        2. Recommend dashboard structure and layout
        3. Suggest interactive elements and user experience features
        4. Ensure accessibility and clarity for target audience
        5. Provide implementation guidance and best practices
        
        DELIVERABLES:
        Please provide a comprehensive analytics report that includes:
        - Executive summary of key findings
        - Detailed analytical methodology and results
        - Statistical validation and confidence measures
        - Business insights and strategic implications
        - Specific, prioritized recommendations
        - Visualization and dashboard specifications
        - Implementation roadmap and next steps
        
        Ensure all findings are well-supported by evidence and clearly communicated.
        """
        
        # Execute the analysis
        result = self.session.execute_crew_task(
            crew_id="advanced_analytics",
            task_description=task_description
        )
        
        return result

def main():
    """Main function demonstrating the analytics crew."""
    
    # Create the analytics crew builder
    builder = AnalyticsCrewBuilder()
    
    # Set up the crew and knowledge base
    crew_id = builder.create_analytics_crew()
    builder.setup_knowledge_base()
    
    print(f"✅ Created analytics crew: {crew_id}")
    
    # Example analysis request
    analysis_request = """
    Analyze customer churn patterns for our SaaS platform. We want to understand:
    1. What factors contribute most to customer churn?
    2. Can we predict which customers are likely to churn?
    3. What interventions might reduce churn rates?
    4. What is the financial impact of different churn scenarios?
    """
    
    data_description = """
    We have customer data including:
    - Demographics (age, location, company size)
    - Usage patterns (login frequency, feature usage, support tickets)
    - Financial data (subscription tier, payment history, discounts)
    - Engagement metrics (training completion, community participation)
    - Churn status and dates
    """
    
    print("🔍 Executing comprehensive churn analysis...")
    
    # Execute the analysis
    result = builder.execute_comprehensive_analysis(
        analysis_request=analysis_request,
        data_description=data_description
    )
    
    print("✅ Analysis complete!")
    print(f"📊 Result: {result['result'][:500]}...")

if __name__ == "__main__":
    main()
```

---

This comprehensive guide provides everything you need to build sophisticated crews and create custom chat flows with Golett AI. The framework's flexibility allows you to create specialized teams for virtually any domain or use case, while the integration with memory and knowledge systems ensures that your crews can learn and improve over time.

Remember to start simple and gradually add complexity as you become more familiar with the system. The key to success is creating clear agent roles, well-structured tasks, and effective coordination between team members. 