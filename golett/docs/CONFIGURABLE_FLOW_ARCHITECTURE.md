# Configurable Flow Architecture for Golett

## Overview

The Configurable Flow Architecture replaces the hardcoded `ChatFlowManager` with a flexible, extensible system that allows domain-specific chatbots to define their own conversation flows without hardcoding business logic.

## Problems with the Original Architecture

The original `ChatFlowManager` had several critical issues:

### 🚫 **Hardcoded Business Logic**
- **BI-Specific Agents**: Hardcoded "BI Query Analyzer", "Response Strategist" agents
- **Fixed Decision Types**: Hardcoded BI data needs analysis and response modes
- **Static Response Modes**: Fixed ANALYTICAL, NARRATIVE, CONVERSATIONAL, INSTRUCTIONAL modes
- **Domain Assumptions**: Assumed all conversations were BI-related

### 🚫 **Lack of Extensibility**
- **No Domain Abstraction**: Couldn't be used for other domains (customer support, e-commerce, etc.)
- **Fixed Flow Stages**: Couldn't add or modify conversation flow stages
- **Hardcoded Task Descriptions**: Task templates were embedded in code
- **No Configuration**: No way to customize agents, tasks, or decision logic

### 🚫 **Maintenance Issues**
- **Monolithic Design**: All logic in one large class
- **Tight Coupling**: Agents, tasks, and decisions tightly coupled to BI domain
- **Code Duplication**: Similar patterns would need to be duplicated for other domains

## New Configurable Architecture

### 🎯 **Core Principles**

1. **Domain Agnostic**: Base classes work for any domain
2. **Configuration-Driven**: Flows defined through configuration, not code
3. **Extensible**: Easy to add new stages, agents, and decision types
4. **Reusable**: Common patterns abstracted for reuse across domains

### 🏗️ **Architecture Components**

```
golett/chat/flow.py
├── FlowStage (Enum)           # Standard flow stages
├── FlowDecision               # Represents flow decisions
├── FlowAgentConfig           # Agent configuration
├── FlowTaskConfig            # Task configuration
├── ChatFlowManagerBase       # Abstract base class
└── SimpleConversationalFlowManager  # Basic implementation
```

## Core Classes

### 1. **FlowStage Enum**

Defines standard stages that can be used across domains:

```python
class FlowStage(Enum):
    ANALYSIS = "analysis"      # Understand the query
    STRATEGY = "strategy"      # Determine response approach
    GENERATION = "generation"  # Generate the response
    VALIDATION = "validation"  # Validate the response
```

### 2. **FlowDecision Class**

Represents decisions made during flow processing:

```python
class FlowDecision:
    def __init__(self, decision_type: str, value: Any, reasoning: str, confidence: float = 1.0):
        self.decision_type = decision_type
        self.value = value
        self.reasoning = reasoning
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()
```

### 3. **FlowAgentConfig Class**

Configuration for creating flow agents:

```python
class FlowAgentConfig:
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        stage: FlowStage,
        tools: List[Any] = None
    ):
        # Configuration for agent creation
```

### 4. **FlowTaskConfig Class**

Configuration for creating flow tasks:

```python
class FlowTaskConfig:
    def __init__(
        self,
        stage: FlowStage,
        description_template: str,
        expected_output: str,
        decision_parser: Callable[[str], FlowDecision] = None
    ):
        # Configuration for task creation with template formatting
```

### 5. **ChatFlowManagerBase (Abstract)**

The abstract base class that provides the configurable framework:

```python
class ChatFlowManagerBase(ABC):
    @abstractmethod
    def _configure_flow(self) -> None:
        """Configure the flow stages, agents, and tasks for this domain"""
        pass
    
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
```

## Creating Domain-Specific Flow Managers

### Example: Business Intelligence Flow Manager

```python
class BIFlowManager(ChatFlowManagerBase):
    def _configure_flow(self) -> None:
        # Stage 1: Data Needs Analysis
        self.add_agent_config(FlowAgentConfig(
            name="BI Data Analyst",
            role="Business Intelligence Data Analyst",
            goal="Determine if queries require BI data and what type of analysis is needed",
            backstory="You are a specialized BI analyst...",
            stage=FlowStage.ANALYSIS,
            tools=self.bi_tools
        ))
        
        self.add_task_config(FlowTaskConfig(
            stage=FlowStage.ANALYSIS,
            description_template="""
            Analyze the user's query to determine BI data requirements.
            
            User query: "{message}"
            Conversation history: {history}
            Available BI context: {context}
            
            Determine:
            1. Does this query require BI data access? (YES/NO)
            2. What type of analysis is needed?
            3. What specific metrics are relevant?
            
            Respond with structured analysis...
            """,
            expected_output="Structured analysis of BI data requirements",
            decision_parser=self._parse_data_analysis_decision
        ))
        
        # Additional stages...
```

### Example: Customer Support Flow Manager

```python
class CustomerSupportFlowManager(ChatFlowManagerBase):
    def _configure_flow(self) -> None:
        # Stage 1: Issue Classification
        self.add_agent_config(FlowAgentConfig(
            name="Support Issue Classifier",
            role="Customer Support Issue Classifier",
            goal="Classify customer issues and determine urgency",
            backstory="You are an expert at understanding customer issues...",
            stage=FlowStage.ANALYSIS,
            tools=self.support_tools
        ))
        
        self.add_task_config(FlowTaskConfig(
            stage=FlowStage.ANALYSIS,
            description_template="""
            Classify the customer's issue and determine appropriate response.
            
            Customer message: "{message}"
            Customer history: {history}
            Available context: {context}
            
            Determine:
            1. What type of issue is this? (technical, billing, general)
            2. What is the urgency level? (low, medium, high, critical)
            3. What resources are needed to resolve this?
            
            Respond with classification...
            """,
            expected_output="Issue classification and urgency assessment",
            decision_parser=self._parse_issue_classification
        ))
```

## Benefits of the New Architecture

### 🚀 **Flexibility**
- **Domain Agnostic**: Works for any domain (BI, support, e-commerce, etc.)
- **Configurable Stages**: Add, remove, or modify flow stages as needed
- **Custom Decision Logic**: Each domain can define its own decision parsing
- **Template-Based Tasks**: Task descriptions use templates with context injection

### 🔧 **Extensibility**
- **Easy Domain Creation**: New domains just inherit and configure
- **Pluggable Components**: Agents, tasks, and parsers are pluggable
- **Tool Integration**: Easy to add domain-specific tools to agents
- **Custom Context**: Each domain can provide its own context retrieval

### 🎯 **Maintainability**
- **Separation of Concerns**: Configuration separated from execution logic
- **Reusable Patterns**: Common patterns abstracted into base classes
- **Clear Abstractions**: Well-defined interfaces for customization
- **Testable Components**: Each component can be tested independently

### 📈 **Scalability**
- **Multiple Domains**: Support unlimited domains without code duplication
- **Parallel Development**: Teams can work on different domains independently
- **Configuration Management**: Flow configurations can be externalized
- **Performance Optimization**: Context retrieval optimized per domain

## Usage Examples

### Basic Usage (General Conversation)

```python
from golett.chat.flow import SimpleConversationalFlowManager

# Create a simple flow manager for general conversation
flow_manager = SimpleConversationalFlowManager(
    session=chat_session,
    domain="general"
)

# Process a message
response = flow_manager.process_user_message("Hello, how can you help me?")
print(response)

# Get flow summary
summary = flow_manager.get_flow_summary()
print(f"Flow stages: {summary['stages']}")
print(f"Decisions: {summary['decisions']}")
```

### Domain-Specific Usage (Business Intelligence)

```python
from golett.domains.business_intelligence import BIFlowManager

# Create BI-specific flow manager with tools
bi_flow_manager = BIFlowManager(
    session=chat_session,
    bi_tools=[BuildCubeQuery(), DataVisualizationTool()],
    llm_model="gpt-4o"
)

# Process BI query
response = bi_flow_manager.process_user_message(
    "What were our sales numbers last quarter?"
)

# Get BI-specific insights
bi_summary = bi_flow_manager.get_bi_flow_summary()
print(f"Data needed: {bi_summary['bi_insights']['data_requirements']['needs_data']}")
print(f"Analysis type: {bi_summary['bi_insights']['data_requirements']['analysis_type']}")
```

### Custom Domain Implementation

```python
class ECommerceFlowManager(ChatFlowManagerBase):
    def __init__(self, session, product_catalog, **kwargs):
        self.product_catalog = product_catalog
        super().__init__(session, domain="e_commerce", **kwargs)
    
    def _configure_flow(self):
        # Configure e-commerce specific flow
        self.add_agent_config(FlowAgentConfig(
            name="Product Specialist",
            role="E-commerce Product Expert",
            goal="Help customers find and understand products",
            backstory="You are an expert in our product catalog...",
            stage=FlowStage.ANALYSIS
        ))
        
        # Add more configurations...
    
    def _get_domain_context(self, message, stage):
        # Get product-specific context
        if "product" in message.lower():
            return self.product_catalog.search(message)
        return []
    
    def _generate_final_response(self, message):
        # Generate e-commerce specific response
        if FlowStage.GENERATION in self.decisions:
            return self.decisions[FlowStage.GENERATION].value
        return "Let me help you find the right product..."
    
    def _get_fallback_decision(self, stage):
        # E-commerce specific fallbacks
        return {"product_search": True, "recommendation_needed": True}

# Usage
ecommerce_flow = ECommerceFlowManager(
    session=session,
    product_catalog=catalog
)
response = ecommerce_flow.process_user_message("I need running shoes")
```

## Migration Guide

### From Old ChatFlowManager

**Before (Hardcoded):**
```python
# Old hardcoded approach
flow_manager = ChatFlowManager(session)
response = flow_manager.process_user_message(message)
```

**After (Configurable):**
```python
# New configurable approach - backward compatible
flow_manager = ChatFlowManager(session)  # Uses SimpleConversationalFlowManager
response = flow_manager.process_user_message(message)

# Or use domain-specific manager
bi_flow_manager = BIFlowManager(session, bi_tools=tools)
response = bi_flow_manager.process_user_message(message)
```

### Creating New Domain Flows

1. **Inherit from ChatFlowManagerBase**
2. **Implement _configure_flow()** - Define agents and tasks
3. **Implement _get_domain_context()** - Provide domain context
4. **Implement _generate_final_response()** - Generate final response
5. **Implement _get_fallback_decision()** - Handle failures gracefully

## Best Practices

### 1. **Flow Configuration**
- **Keep stages focused**: Each stage should have a single responsibility
- **Use clear naming**: Agent and task names should be descriptive
- **Provide rich backstories**: Help agents understand their role and capabilities
- **Include relevant tools**: Provide agents with the tools they need

### 2. **Decision Parsing**
- **Structure decisions**: Use consistent formats for decision parsing
- **Include confidence**: Provide confidence scores for decisions
- **Handle errors**: Gracefully handle parsing failures
- **Document formats**: Clearly document expected decision formats

### 3. **Context Management**
- **Stage-specific context**: Provide relevant context for each stage
- **Optimize retrieval**: Don't retrieve unnecessary context
- **Cache when appropriate**: Cache expensive context operations
- **Handle failures**: Gracefully handle context retrieval failures

### 4. **Error Handling**
- **Provide fallbacks**: Always have fallback decisions for failures
- **Log appropriately**: Log errors for debugging and improvement
- **Graceful degradation**: Continue processing even if stages fail
- **User-friendly messages**: Provide helpful error messages to users

## Future Enhancements

### 1. **External Configuration**
- **YAML/JSON configs**: Move flow configurations to external files
- **Dynamic loading**: Load configurations at runtime
- **Configuration validation**: Validate configurations before use
- **Hot reloading**: Update configurations without restart

### 2. **Advanced Features**
- **Conditional stages**: Skip stages based on conditions
- **Parallel processing**: Process multiple stages in parallel
- **Stage dependencies**: Define dependencies between stages
- **Custom stage types**: Allow custom stage types beyond the standard ones

### 3. **Monitoring and Analytics**
- **Flow metrics**: Track stage performance and success rates
- **Decision analytics**: Analyze decision patterns and accuracy
- **A/B testing**: Test different flow configurations
- **Performance optimization**: Optimize based on usage patterns

This configurable architecture transforms Golett's flow management from a hardcoded, BI-specific system into a flexible, extensible platform that can support any domain while maintaining the power and sophistication of the original system. 