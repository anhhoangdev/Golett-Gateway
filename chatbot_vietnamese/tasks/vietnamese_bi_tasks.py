"""
Vietnamese Business Intelligence Tasks

This module contains task definitions for the Vietnamese BI chatbot,
properly integrated with Golett's core memory and context management capabilities.
"""

from typing import Dict, Any, List, Optional
from crewai import Task, Agent
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.contextual.context_manager import ContextManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class VietnameseTaskFactory:
    """
    Factory class for creating Vietnamese BI tasks with proper Golett integration
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        context_manager: ContextManager,
        session_id: str
    ):
        """
        Initialize task factory
        
        Args:
            memory_manager: Golett memory manager instance
            context_manager: Golett context manager instance
            session_id: Current session ID
        """
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
    
    def create_classification_task(self, question: str, agent: Agent) -> Task:
        """Create conversation classification task"""
        return ConversationClassificationTask(
            question=question,
            agent=agent,
            memory_manager=self.memory_manager,
            session_id=self.session_id
        ).create()
    
    def create_data_analysis_task(
        self, 
        question: str, 
        agent: Agent,
        enhanced_context: Dict[str, Any]
    ) -> Task:
        """Create data analysis task with enhanced Golett context"""
        return DataAnalysisTask(
            question=question,
            agent=agent,
            enhanced_context=enhanced_context,
            memory_manager=self.memory_manager,
            context_manager=self.context_manager,
            session_id=self.session_id
        ).create()
    
    def create_follow_up_task(
        self, 
        question: str, 
        agent: Agent,
        enhanced_context: Dict[str, Any]
    ) -> Task:
        """Create follow-up task with Golett context"""
        return FollowUpTask(
            question=question,
            agent=agent,
            enhanced_context=enhanced_context,
            memory_manager=self.memory_manager,
            context_manager=self.context_manager,
            session_id=self.session_id
        ).create()
    
    def create_conversational_task(
        self, 
        question: str, 
        agent: Agent,
        conversation_context: List[Dict[str, Any]],
        enhanced_context: Dict[str, Any] = None
    ) -> Task:
        """Create conversational task with enhanced context"""
        return ConversationalTask(
            question=question,
            agent=agent,
            conversation_context=conversation_context,
            memory_manager=self.memory_manager,
            session_id=self.session_id,
            enhanced_context=enhanced_context
        ).create()
    
    def create_explanation_task(
        self, 
        question: str, 
        agent: Agent,
        enhanced_context: Dict[str, Any]
    ) -> Task:
        """Create explanation task with Golett context"""
        return ExplanationTask(
            question=question,
            agent=agent,
            enhanced_context=enhanced_context,
            memory_manager=self.memory_manager,
            context_manager=self.context_manager,
            session_id=self.session_id
        ).create()


class ConversationClassificationTask:
    """Task for classifying conversation types"""
    
    def __init__(
        self,
        question: str,
        agent: Agent,
        memory_manager: MemoryManager,
        session_id: str
    ):
        self.question = question
        self.agent = agent
        self.memory_manager = memory_manager
        self.session_id = session_id
    
    def create(self) -> Task:
        """Create the classification task"""
        
        # Get recent conversation context for better classification
        recent_context = self._get_recent_context()
        
        return Task(
            description=f"""
Classify this Vietnamese question to determine the conversation flow type: "{self.question}"

RECENT CONVERSATION CONTEXT FROM GOLETT MEMORY:
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
1. Analyze the question content and intent using Golett memory context
2. Consider the conversation context from previous interactions
3. Choose the MOST APPROPRIATE single classification
4. Respond with ONLY the classification type: data_analysis, follow_up, conversational, or clarification

RESPOND WITH ONLY ONE WORD: data_analysis, follow_up, conversational, or clarification
""",
            agent=self.agent,
            expected_output="Single word classification: data_analysis, follow_up, conversational, or clarification"
        )
    
    def _get_recent_context(self) -> str:
        """Get recent conversation context from Golett memory"""
        try:
            recent_messages = self.memory_manager.get_session_history(
                session_id=self.session_id,
                limit=5,
                include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
            )
            
            if not recent_messages:
                return "No previous conversation context."
            
            context_parts = ["RECENT CONVERSATION:"]
            for msg in recent_messages[-3:]:  # Last 3 messages
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:150]
                context_parts.append(f"{role.upper()}: {content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"Error getting recent context: {e}")
            return "Error retrieving conversation context."


class DataAnalysisTask:
    """Task for data analysis with enhanced Golett context"""
    
    def __init__(
        self,
        question: str,
        agent: Agent,
        enhanced_context: Dict[str, Any],
        memory_manager: MemoryManager,
        context_manager: ContextManager,
        session_id: str
    ):
        self.question = question
        self.agent = agent
        self.enhanced_context = enhanced_context
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
    
    def create(self) -> Task:
        """Create the data analysis task"""
        
        # Format enhanced context from Golett
        formatted_context = self._format_enhanced_context()
        
        return Task(
            description=f"""
Answer this Vietnamese business question: "{self.question}"

ENHANCED GOLETT CONTEXT:
{formatted_context}

CRITICAL CUBEJS QUERY LIMITATIONS & RULES (MUST FOLLOW):

🚨 SINGLE CUBE LIMITATION:
- CubeJS can ONLY query ONE CUBE at a time
- You CANNOT join multiple cubes in a single query
- If you need data from multiple cubes, perform SEPARATE queries for each cube

QUERY FORMAT RULES:
1. Time dimensions MUST use "dimension" field: {{"dimension": "cube.field", "granularity": "month"}}
2. Filters MUST use "member" field: {{"member": "cube.field", "operator": "equals", "values": ["value"]}}
3. Always use cube prefixes: "cube_name.field_name"
4. Available time granularities: day, week, month, quarter, year

INSTRUCTIONS:
1. Use Golett's enhanced context to understand the business question better
2. Identify which cube(s) contain the data you need
3. For EACH cube, use BuildCubeQuery to create a separate query
4. Use ExecuteCubeQuery to get data from each cube separately
5. Use AnalyzeDataPoint to analyze each result
6. Combine insights from multiple cubes in your final answer
7. Reference relevant business intelligence context from Golett memory
8. Store important insights back to Golett memory for future reference
9. Provide a comprehensive answer in Vietnamese

Remember: Leverage Golett's context for intelligent, context-aware responses!
            """,
            expected_output="Comprehensive Vietnamese answer with data analysis and Golett memory context integration",
            agent=self.agent
        )
    
    def _format_enhanced_context(self) -> str:
        """Format enhanced context from Golett with semantic memory retrieval"""
        context_parts = []
        
        # BI Context (existing)
        bi_context = self.enhanced_context.get("bi_context", [])
        if bi_context:
            context_parts.append("📊 RELEVANT BUSINESS INTELLIGENCE FROM GOLETT:")
            for item in bi_context[:3]:
                data = str(item.get("data", ""))[:200]
                description = item.get("metadata", {}).get("description", "")
                context_parts.append(f"- {description}: {data}")
        
        # Knowledge Context (existing)
        knowledge_context = self.enhanced_context.get("knowledge_context", [])
        if knowledge_context:
            context_parts.append("\n📚 RELEVANT CUBEJS KNOWLEDGE FROM GOLETT:")
            for item in knowledge_context[:2]:
                content = str(item.get("content", item.get("data", "")))[:300]
                context_parts.append(f"- {content}")
        
        # NEW: Semantic Memories from Qdrant
        semantic_memories = self.enhanced_context.get("semantic_memories", [])
        if semantic_memories:
            context_parts.append("\n🧠 SEMANTIC MEMORIES FROM QDRANT (Similar Past Interactions):")
            for memory in semantic_memories[:3]:
                content = str(memory.get("content", ""))[:250]
                similarity = memory.get("similarity_score", 0.0)
                layer = memory.get("memory_layer", "unknown")
                timestamp = memory.get("timestamp", "")[:10]  # Just date
                context_parts.append(f"- [{layer}] ({similarity:.2f} similarity, {timestamp}): {content}")
        
        # NEW: Cross-Session Business Insights
        cross_session_insights = self.enhanced_context.get("cross_session_insights", [])
        if cross_session_insights:
            context_parts.append("\n🔄 CROSS-SESSION BUSINESS INSIGHTS:")
            for insight in cross_session_insights[:2]:
                insight_text = str(insight.get("insight", ""))[:200]
                importance = insight.get("importance", 0.0)
                source_session = insight.get("source_session", "unknown")[:8]  # Short session ID
                context_parts.append(f"- [Session: {source_session}] (Importance: {importance:.1f}): {insight_text}")
        
        # NEW: Related Conversation Summaries
        related_summaries = self.enhanced_context.get("related_summaries", [])
        if related_summaries:
            context_parts.append("\n💬 RELATED PAST CONVERSATIONS:")
            for summary in related_summaries[:2]:
                summary_text = str(summary.get("summary", ""))[:200]
                topics = summary.get("topics", [])
                topics_str = ", ".join(topics[:3]) if topics else "general"
                context_parts.append(f"- Topics: [{topics_str}]: {summary_text}")
        
        # Recent Conversation Context (enhanced)
        recent_conversation = self.enhanced_context.get("recent_conversation", [])
        if recent_conversation:
            context_parts.append("\n💭 RECENT CONVERSATION FROM CURRENT SESSION:")
            for msg in recent_conversation[-3:]:
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:150]
                context_parts.append(f"- {role.upper()}: {content}")
        
        return "\n".join(context_parts) if context_parts else "No enhanced context available."


class FollowUpTask:
    """Task for handling follow-up questions with Golett context"""
    
    def __init__(
        self,
        question: str,
        agent: Agent,
        enhanced_context: Dict[str, Any],
        memory_manager: MemoryManager,
        context_manager: ContextManager,
        session_id: str
    ):
        self.question = question
        self.agent = agent
        self.enhanced_context = enhanced_context
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
    
    def create(self) -> Task:
        """Create the follow-up task"""
        
        formatted_context = self._format_follow_up_context()
        
        return Task(
            description=f"""
Answer this Vietnamese follow-up question: "{self.question}"

ENHANCED GOLETT CONTEXT FOR FOLLOW-UP:
{formatted_context}

INSTRUCTIONS:
1. Use Golett's enhanced context to understand the follow-up question in relation to previous conversation
2. Reference previous data analysis results stored in Golett memory
3. Provide additional insights based on business intelligence context
4. If the follow-up requires new data analysis, suggest asking a more specific question
5. Be conversational and helpful while leveraging Golett's memory capabilities
6. Reference cross-session knowledge when relevant

Answer in Vietnamese with context-aware insights from Golett memory.
""",
            agent=self.agent,
            expected_output="A helpful Vietnamese response to the follow-up question with Golett context integration"
        )
    
    def _format_follow_up_context(self) -> str:
        """Format context specifically for follow-up questions with semantic memory"""
        context_parts = []
        
        # Recent conversation with more detail for follow-ups
        recent_conversation = self.enhanced_context.get("recent_conversation", [])
        if recent_conversation:
            context_parts.append("💭 RECENT CONVERSATION FROM CURRENT SESSION:")
            for msg in recent_conversation[-5:]:  # More context for follow-ups
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:250]  # More content for follow-ups
                context_parts.append(f"- {role.upper()}: {content}")
        
        # Semantic memories focused on recent interactions
        semantic_memories = self.enhanced_context.get("semantic_memories", [])
        if semantic_memories:
            context_parts.append("\n🧠 RELATED MEMORIES FROM RECENT SESSIONS:")
            for memory in semantic_memories[:3]:
                content = str(memory.get("content", ""))[:200]
                similarity = memory.get("similarity_score", 0.0)
                layer = memory.get("memory_layer", "unknown")
                context_parts.append(f"- [{layer}] ({similarity:.2f} similarity): {content}")
        
        # BI Context for reference
        bi_context = self.enhanced_context.get("bi_context", [])
        if bi_context:
            context_parts.append("\n📊 RELATED BUSINESS INSIGHTS:")
            for item in bi_context[:2]:
                data = str(item.get("data", ""))[:200]
                context_parts.append(f"- {data}")
        
        return "\n".join(context_parts) if context_parts else "No follow-up context available."


class ConversationalTask:
    """Task for general conversational interactions"""
    
    def __init__(
        self,
        question: str,
        agent: Agent,
        conversation_context: List[Dict[str, Any]],
        memory_manager: MemoryManager,
        session_id: str,
        enhanced_context: Dict[str, Any] = None
    ):
        self.question = question
        self.agent = agent
        self.conversation_context = conversation_context
        self.memory_manager = memory_manager
        self.session_id = session_id
        self.enhanced_context = enhanced_context or {}
    
    def create(self) -> Task:
        """Create the conversational task"""
        
        formatted_context = self._format_conversation_context()
        
        return Task(
            description=f"""
Respond to this Vietnamese conversational question: "{self.question}"

CONVERSATION CONTEXT FROM GOLETT:
{formatted_context}

INSTRUCTIONS:
1. Be friendly and helpful in Vietnamese
2. Use Golett memory context to provide personalized responses
3. If it's a greeting, respond warmly and reference past interactions if relevant
4. If it's a question about capabilities, explain what you can do with business data
5. If it's a thank you, acknowledge gracefully
6. If it's about business intelligence, provide helpful guidance
7. Encourage users to ask specific business questions for data analysis
8. Reference user preferences or past conversations stored in Golett memory when appropriate

CAPABILITIES TO MENTION (if relevant):
- Analyze business data (doanh thu, bán hàng, tài chính, sản xuất, nhân sự)
- Create reports and insights with memory of past analyses
- Answer questions about trends, comparisons, and performance
- Help with Vietnamese business intelligence queries
- Remember and build upon previous conversations

Answer in Vietnamese with a friendly, professional tone using Golett memory insights.
""",
            agent=self.agent,
            expected_output="A friendly Vietnamese conversational response with Golett memory integration"
        )
    
    def _format_conversation_context(self) -> str:
        """Format conversation context with user preferences and memory lookup"""
        context_parts = []
        
        # Recent conversation from current session
        if not self.conversation_context:
            context_parts.append("No previous conversation context in current session.")
        else:
            context_parts.append("💭 RECENT CONVERSATION FROM CURRENT SESSION:")
            for msg in self.conversation_context[-3:]:
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:150]
                context_parts.append(f"- {role.upper()}: {content}")
        
        # User preferences from enhanced context (if available)
        if hasattr(self, 'enhanced_context') and self.enhanced_context:
            user_preferences = self.enhanced_context.get("user_preferences", [])
            if user_preferences:
                context_parts.append("\n👤 USER PREFERENCES AND PAST INTERACTIONS:")
                for pref in user_preferences[:2]:
                    content = str(pref.get("content", ""))[:150]
                    similarity = pref.get("similarity_score", 0.0)
                    context_parts.append(f"- ({similarity:.2f} similarity): {content}")
        
        return "\n".join(context_parts)


class ExplanationTask:
    """Task for providing explanations and clarifications with Golett context"""
    
    def __init__(
        self,
        question: str,
        agent: Agent,
        enhanced_context: Dict[str, Any],
        memory_manager: MemoryManager,
        context_manager: ContextManager,
        session_id: str
    ):
        self.question = question
        self.agent = agent
        self.enhanced_context = enhanced_context
        self.memory_manager = memory_manager
        self.context_manager = context_manager
        self.session_id = session_id
    
    def create(self) -> Task:
        """Create the explanation task"""
        
        formatted_context = self._format_explanation_context()
        
        return Task(
            description=f"""
Provide a clear explanation for this Vietnamese question: "{self.question}"

ENHANCED GOLETT CONTEXT FOR EXPLANATION:
{formatted_context}

INSTRUCTIONS:
1. Use Golett's enhanced context to understand what the user is asking for clarification about
2. Reference previous explanations stored in Golett memory to build upon them
3. Provide a clear, detailed explanation in Vietnamese
4. Use simple language and examples when possible
5. If it's about previous data analysis, explain the results clearly using stored context
6. If it's about business concepts, provide educational content
7. Reference business intelligence insights from Golett memory when relevant
8. Store important explanations back to Golett memory for future reference
9. Be thorough but easy to understand

Answer in Vietnamese with clear explanations enhanced by Golett memory context.
""",
            agent=self.agent,
            expected_output="A clear Vietnamese explanation answering the clarification question with Golett context integration"
        )
    
    def _format_explanation_context(self) -> str:
        """Format context for explanations with comprehensive memory lookup"""
        context_parts = []
        
        # Recent conversation context for understanding what needs explanation
        recent_conversation = self.enhanced_context.get("recent_conversation", [])
        if recent_conversation:
            context_parts.append("💭 RECENT CONVERSATION CONTEXT:")
            for msg in recent_conversation[-4:]:
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:200]
                context_parts.append(f"- {role.upper()}: {content}")
        
        # Semantic memories for related explanations and concepts
        semantic_memories = self.enhanced_context.get("semantic_memories", [])
        if semantic_memories:
            context_parts.append("\n🧠 RELATED MEMORIES AND PAST EXPLANATIONS:")
            for memory in semantic_memories[:4]:  # More memories for explanations
                content = str(memory.get("content", ""))[:250]
                similarity = memory.get("similarity_score", 0.0)
                layer = memory.get("memory_layer", "unknown")
                context_type = memory.get("context_type", "general")
                context_parts.append(f"- [{layer}] {context_type} ({similarity:.2f}): {content}")
        
        # Cross-session insights for broader understanding
        cross_session_insights = self.enhanced_context.get("cross_session_insights", [])
        if cross_session_insights:
            context_parts.append("\n🔄 INSIGHTS FROM OTHER SESSIONS:")
            for insight in cross_session_insights[:2]:
                insight_text = str(insight.get("insight", ""))[:200]
                importance = insight.get("importance", 0.0)
                context_parts.append(f"- (Importance: {importance:.1f}): {insight_text}")
        
        # Business intelligence context for technical explanations
        bi_context = self.enhanced_context.get("bi_context", [])
        if bi_context:
            context_parts.append("\n📊 BUSINESS INTELLIGENCE CONTEXT:")
            for item in bi_context[:3]:
                data = str(item.get("data", ""))[:200]
                description = item.get("metadata", {}).get("description", "")
                context_parts.append(f"- {description}: {data}")
        
        # Knowledge context for technical concepts
        knowledge_context = self.enhanced_context.get("knowledge_context", [])
        if knowledge_context:
            context_parts.append("\n📚 TECHNICAL KNOWLEDGE CONTEXT:")
            for item in knowledge_context[:2]:
                content = str(item.get("content", item.get("data", "")))[:250]
                context_parts.append(f"- {content}")
        
        # Related conversation summaries for broader context
        related_summaries = self.enhanced_context.get("related_summaries", [])
        if related_summaries:
            context_parts.append("\n💬 RELATED PAST CONVERSATIONS:")
            for summary in related_summaries[:2]:
                summary_text = str(summary.get("summary", ""))[:200]
                topics = summary.get("topics", [])
                topics_str = ", ".join(topics[:3]) if topics else "general"
                context_parts.append(f"- Topics: [{topics_str}]: {summary_text}")
        
        return "\n".join(context_parts) if context_parts else "No explanation context available." 