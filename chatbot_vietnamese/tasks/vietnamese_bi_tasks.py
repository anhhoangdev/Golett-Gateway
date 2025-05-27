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
import json

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

🚨 MANDATORY TOOL USAGE REQUIREMENTS (ABSOLUTELY REQUIRED):

YOU MUST USE THE FOLLOWING TOOLS IN THIS EXACT ORDER:
1. BuildCubeQuery - MANDATORY to build the query
2. ExecuteCubeQuery - MANDATORY to get actual data
3. AnalyzeDataPoint - MANDATORY to analyze the results

🚫 STRICTLY FORBIDDEN:
- Answering without using tools
- Making up data or numbers
- Providing generic responses
- Hallucinating business insights
- Returning responses like "Tôi đã tổng hợp và phân tích..." without actual data

✅ VALIDATION CHECKLIST (YOU MUST VERIFY):
- Did I use BuildCubeQuery to create a proper query?
- Did I use ExecuteCubeQuery to get real data from the API?
- Did I use AnalyzeDataPoint to analyze the actual results?
- Do I have real numbers and data points in my response?
- Am I providing specific insights based on actual data?

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

🚨 CRITICAL OUTPUT REQUIREMENTS (MUST FOLLOW):
- DO NOT return raw tool outputs or JSON data
- DO NOT return query objects or technical data structures
- ALWAYS process tool results into human-readable Vietnamese summaries
- ALWAYS provide business insights and analysis in Vietnamese
- ALWAYS explain what the data means for the business
- ALWAYS include specific numbers and data points from the actual query results

MANDATORY STEP-BY-STEP PROCESS (NO SHORTCUTS ALLOWED):
1. Use Golett's enhanced context to understand the business question better
2. Identify which cube(s) contain the data you need
3. For EACH cube, use BuildCubeQuery to create a separate query (MANDATORY)
4. Use ExecuteCubeQuery to get data from each cube separately (MANDATORY)
5. Use AnalyzeDataPoint to analyze each result (MANDATORY)
6. **MOST IMPORTANT**: Process ALL tool outputs into a comprehensive Vietnamese business analysis
7. Combine insights from multiple cubes in your final answer
8. Reference relevant business intelligence context from Golett memory
9. Store important insights back to Golett memory for future reference

REQUIRED OUTPUT FORMAT (MUST INCLUDE ACTUAL DATA):
📊 **Phân tích dữ liệu kinh doanh:**
[Provide Vietnamese summary of the ACTUAL data findings with specific numbers]

💡 **Insights và nhận định:**
[Provide business insights based on REAL data and what the data means]

📈 **Khuyến nghị:**
[Provide actionable recommendations based on ACTUAL analysis results]

🔍 **Dữ liệu cụ thể:**
[Include specific data points, numbers, and metrics from the query results]

FINAL VALIDATION BEFORE RESPONDING:
- Can I point to specific numbers in my response that came from the tools?
- Did I actually execute queries and get real data?
- Am I providing insights based on actual analysis, not generic statements?
- Would someone reading this know exactly what data I found?

Remember: 
- TOOL USAGE IS MANDATORY - NO EXCEPTIONS
- NEVER return raw tool data or JSON objects
- ALWAYS provide Vietnamese business analysis and insights
- ALWAYS explain the business meaning of the data
- ALWAYS include specific data points and numbers from actual queries
- Leverage Golett's context for intelligent, context-aware responses!
            """,
            expected_output="Comprehensive Vietnamese business analysis with insights and recommendations based on ACTUAL data from mandatory tool usage (NO raw tool data or JSON, NO generic responses without real data)",
            agent=self.agent
        )
    
    def _format_enhanced_context(self) -> str:
        """Format enhanced context from Golett with semantic memory retrieval"""
        context_parts = []
        
        # Enhanced SHORT-TERM Context with semantic search results
        short_term_summaries = self.enhanced_context.get("short_term_summaries", [])
        if short_term_summaries:
            context_parts.append("📊 ENHANCED SHORT-TERM BUSINESS INTELLIGENCE (Semantic Search):")
            for summary in short_term_summaries[:3]:
                content = str(summary.get("content", ""))[:200]
                summary_type = summary.get("summary_type", "unknown")
                similarity = summary.get("similarity_score", 0.0)
                relevance = summary.get("relevance_reason", "")
                search_method = summary.get("search_method", "unknown")
                
                # Show semantic search quality
                quality_emoji = "🎯" if similarity > 0.7 else "🔍" if similarity > 0.5 else "📝"
                context_parts.append(f"- {quality_emoji} [{summary_type}] (Similarity: {similarity:.2f}): {content}")
                if relevance:
                    context_parts.append(f"  └─ Why relevant: {relevance}")
                context_parts.append(f"  └─ Search: {search_method}")
        
        # Enhanced LONG-TERM Context with cross-session insights
        long_term_insights = self.enhanced_context.get("long_term_insights", [])
        if long_term_insights:
            context_parts.append("\n🧠 ENHANCED LONG-TERM INSIGHTS (Cross-Session Semantic Search):")
            for insight in long_term_insights[:2]:
                content = str(insight.get("content", ""))[:200]
                insight_type = insight.get("insight_type", "unknown")
                similarity = insight.get("similarity_score", 0.0)
                cross_session = insight.get("cross_session", False)
                relevance = insight.get("relevance_reason", "")
                domain = insight.get("domain", "unknown")
                
                # Show cross-session and quality indicators
                session_emoji = "🔄" if cross_session else "📍"
                quality_emoji = "🎯" if similarity > 0.7 else "🔍" if similarity > 0.5 else "📝"
                context_parts.append(f"- {session_emoji}{quality_emoji} [{insight_type}] (Similarity: {similarity:.2f}): {content}")
                if domain != "unknown":
                    context_parts.append(f"  └─ Domain: {domain}")
                if relevance:
                    context_parts.append(f"  └─ Why relevant: {relevance}")
                if cross_session:
                    context_parts.append(f"  └─ Source: Cross-session insight")
        
        # BI Context (existing - for backward compatibility)
        bi_context = self.enhanced_context.get("bi_context", [])
        if bi_context:
            context_parts.append("\n📊 RELEVANT BUSINESS INTELLIGENCE FROM GOLETT:")
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
        
        # Recent Conversation Context (enhanced)
        recent_conversation = self.enhanced_context.get("recent_conversation", [])
        if recent_conversation:
            context_parts.append("\n💭 RECENT CONVERSATION FROM CURRENT SESSION:")
            for msg in recent_conversation[-3:]:
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:150]
                context_parts.append(f"- {role.upper()}: {content}")
        
        # Add semantic search metadata summary
        retrieval_metadata = self.enhanced_context.get("retrieval_metadata", {})
        if retrieval_metadata:
            context_parts.append(f"\n🔍 SEMANTIC SEARCH SUMMARY:")
            context_parts.append(f"- Strategy: {retrieval_metadata.get('strategy', 'unknown')}")
            context_parts.append(f"- Used Short-term: {retrieval_metadata.get('used_short_term', False)}")
            context_parts.append(f"- Used Long-term: {retrieval_metadata.get('used_long_term', False)}")
            
            # Calculate average similarity if available
            if short_term_summaries:
                avg_short_sim = sum(s.get("similarity_score", 0.0) for s in short_term_summaries) / len(short_term_summaries)
                context_parts.append(f"- Short-term avg similarity: {avg_short_sim:.2f}")
            if long_term_insights:
                avg_long_sim = sum(i.get("similarity_score", 0.0) for i in long_term_insights) / len(long_term_insights)
                cross_session_count = sum(1 for i in long_term_insights if i.get("cross_session", False))
                context_parts.append(f"- Long-term avg similarity: {avg_long_sim:.2f}")
                context_parts.append(f"- Cross-session insights: {cross_session_count}/{len(long_term_insights)}")
        
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

IN-MEMORY SESSION CONTEXT FOR FOLLOW-UP:
{formatted_context}

FOLLOW-UP PROCESSING INSTRUCTIONS:
1. Use ONLY the in-memory context from the current session - no cross-session data
2. Search within the current conversation for relevant information
3. Reference previous messages and responses from this session
4. Build upon the immediate conversation context
5. If the follow-up asks for more details, elaborate on previous responses
6. If the follow-up asks for clarification, explain previous answers more clearly
7. Stay focused on the current session's conversation flow
8. Do not retrieve information from other sessions or long-term memory

FOLLOW-UP RESPONSE GUIDELINES:
- Be conversational and reference the immediate context
- Provide the additional details or clarification requested
- If previous data analysis was mentioned, elaborate on those specific results
- If no relevant context is found in current session, ask for clarification
- Keep responses focused on the current conversation thread

Answer in Vietnamese with context-aware insights from the current session only.
""",
            agent=self.agent,
            expected_output="A helpful Vietnamese response to the follow-up question using only current session context"
        )
    
    def _format_follow_up_context(self) -> str:
        """Format enhanced follow-up context with semantic search results"""
        context_parts = []
        
        # Enhanced SHORT-TERM Context for follow-up
        short_term_summaries = self.enhanced_context.get("short_term_summaries", [])
        if short_term_summaries:
            context_parts.append("🔄 ENHANCED SHORT-TERM FOLLOW-UP CONTEXT (Semantic Search):")
            for summary in short_term_summaries[:3]:
                content = str(summary.get("content", ""))[:200]
                summary_type = summary.get("summary_type", "unknown")
                similarity = summary.get("similarity_score", 0.0)
                relevance = summary.get("relevance_reason", "")
                search_method = summary.get("search_method", "unknown")
                
                # Show semantic search quality for follow-up
                quality_emoji = "🎯" if similarity > 0.7 else "🔍" if similarity > 0.5 else "📝"
                context_parts.append(f"- {quality_emoji} [{summary_type}] (Similarity: {similarity:.2f}): {content}")
                if relevance:
                    context_parts.append(f"  └─ Follow-up relevance: {relevance}")
                context_parts.append(f"  └─ Search method: {search_method}")
        
        # Enhanced LONG-TERM Context for historical follow-up patterns
        long_term_insights = self.enhanced_context.get("long_term_insights", [])
        if long_term_insights:
            context_parts.append("\n🧠 ENHANCED LONG-TERM FOLLOW-UP PATTERNS (Cross-Session):")
            for insight in long_term_insights[:2]:
                content = str(insight.get("content", ""))[:200]
                insight_type = insight.get("insight_type", "unknown")
                similarity = insight.get("similarity_score", 0.0)
                cross_session = insight.get("cross_session", False)
                relevance = insight.get("relevance_reason", "")
                domain = insight.get("domain", "unknown")
                
                # Show cross-session follow-up patterns
                session_emoji = "🔄" if cross_session else "📍"
                quality_emoji = "🎯" if similarity > 0.7 else "🔍" if similarity > 0.5 else "📝"
                context_parts.append(f"- {session_emoji}{quality_emoji} [{insight_type}] (Similarity: {similarity:.2f}): {content}")
                if domain != "unknown":
                    context_parts.append(f"  └─ Domain: {domain}")
                if relevance:
                    context_parts.append(f"  └─ Follow-up pattern: {relevance}")
                if cross_session:
                    context_parts.append(f"  └─ Historical pattern from previous sessions")
        
        # Enhanced session search results with semantic scoring
        session_search_results = self.enhanced_context.get("session_search_results", [])
        if session_search_results:
            context_parts.append("\n🔍 ENHANCED SESSION SEARCH RESULTS (Semantic Follow-up Search):")
            for result in session_search_results:
                content = str(result.get("content", ""))[:200]
                similarity = result.get("similarity_score", 0.0)
                search_method = result.get("search_method", "unknown")
                relevance = result.get("relevance_reason", "")
                timestamp = result.get("timestamp", "")[:16] if result.get("timestamp") else ""
                
                # Show semantic search quality for session results
                quality_emoji = "🎯" if similarity > 0.7 else "🔍" if similarity > 0.5 else "📝"
                context_parts.append(f"- {quality_emoji} (Similarity: {similarity:.2f}) [{timestamp}]: {content}")
                if relevance:
                    context_parts.append(f"  └─ Why relevant for follow-up: {relevance}")
                context_parts.append(f"  └─ Found via: {search_method}")
        
        # Recent conversation context (enhanced)
        recent_conversation = self.enhanced_context.get("recent_conversation", [])
        if recent_conversation:
            context_parts.append("\n💭 RECENT CONVERSATION CONTEXT:")
            for msg in recent_conversation[-4:]:
                role = msg.get("metadata", {}).get("role", "unknown")
                content = str(msg.get("data", ""))[:150]
                timestamp = msg.get("metadata", {}).get("timestamp", "")[:16] if msg.get("metadata", {}).get("timestamp") else ""
                context_parts.append(f"- [{timestamp}] {role.upper()}: {content}")
        
        # Add semantic follow-up search metadata
        retrieval_metadata = self.enhanced_context.get("retrieval_metadata", {})
        if retrieval_metadata:
            context_parts.append(f"\n🔍 SEMANTIC FOLLOW-UP SEARCH SUMMARY:")
            context_parts.append(f"- Strategy: {retrieval_metadata.get('strategy', 'unknown')}")
            context_parts.append(f"- Conversation type: {retrieval_metadata.get('conversation_type', 'unknown')}")
            context_parts.append(f"- Used Short-term: {retrieval_metadata.get('used_short_term', False)}")
            context_parts.append(f"- Used Long-term: {retrieval_metadata.get('used_long_term', False)}")
            
            # Calculate follow-up specific similarity metrics
            if short_term_summaries:
                avg_short_sim = sum(s.get("similarity_score", 0.0) for s in short_term_summaries) / len(short_term_summaries)
                context_parts.append(f"- Short-term follow-up similarity: {avg_short_sim:.2f}")
            if long_term_insights:
                avg_long_sim = sum(i.get("similarity_score", 0.0) for i in long_term_insights) / len(long_term_insights)
                cross_session_count = sum(1 for i in long_term_insights if i.get("cross_session", False))
                context_parts.append(f"- Long-term follow-up similarity: {avg_long_sim:.2f}")
                context_parts.append(f"- Cross-session follow-up patterns: {cross_session_count}/{len(long_term_insights)}")
            if session_search_results:
                avg_session_sim = sum(r.get("similarity_score", 0.0) for r in session_search_results) / len(session_search_results)
                context_parts.append(f"- Session search similarity: {avg_session_sim:.2f}")
        
        return "\n".join(context_parts) if context_parts else "No enhanced follow-up context available."


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