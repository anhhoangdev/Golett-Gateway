#!/usr/bin/env python3
"""
Memory Decision Agent for Vietnamese Business Intelligence Chatbot

This agent makes intelligent decisions about memory layer storage:
- Long-term: Business domain knowledge, company states, strategic insights
- Short-term: BI context importance, session-specific analysis, tactical insights

The agent analyzes conversation content, business context, and importance to determine
the appropriate memory layer and storage strategy.
"""

import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from crewai import Agent, Task
from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.contextual.context_manager import ContextManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryDecisionType(Enum):
    """Types of memory decisions the agent can make"""
    STORE_LONG_TERM = "store_long_term"
    STORE_SHORT_TERM = "store_short_term"
    STORE_IN_SESSION = "store_in_session"
    NO_STORAGE = "no_storage"
    MIGRATE_TO_LONG_TERM = "migrate_to_long_term"
    MIGRATE_TO_SHORT_TERM = "migrate_to_short_term"


class BusinessDomainType(Enum):
    """Types of business domain knowledge for LONG-TERM storage"""
    COMPANY_STATE = "company_state"           # Company performance, health, status
    STRATEGIC_INSIGHT = "strategic_insight"   # Long-term business strategy insights
    MARKET_ANALYSIS = "market_analysis"       # Market trends, competitive analysis
    BUSINESS_RULE = "business_rule"          # Business rules and policies
    DOMAIN_KNOWLEDGE = "domain_knowledge"     # General business domain knowledge
    INDUSTRY_KNOWLEDGE = "industry_knowledge" # Industry-specific knowledge
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence" # Competitor analysis


class OperationalStateType(Enum):
    """Types of operational states that should go to IN_SESSION memory"""
    SESSION_STATE = "session_state"
    CREW_CONFIG = "crew_config"
    AGENT_CONFIG = "agent_config"
    WORKFLOW_STATE = "workflow_state"
    SYSTEM_STATE = "system_state"
    TEMPORARY_CONFIG = "temporary_config"
    CONVERSATION_FLOW = "conversation_flow"


class BIContextType(Enum):
    """Types of BI context and operational business insights for SHORT-TERM storage"""
    OPERATIONAL_INSIGHT = "operational_insight"     # Current operational performance insights
    TACTICAL_ANALYSIS = "tactical_analysis"         # Short-term tactical business analysis
    DATA_DISCOVERY = "data_discovery"               # Data exploration findings
    QUERY_PATTERN = "query_pattern"                 # User query patterns and preferences
    BI_RESULT = "bi_result"                        # BI analysis results
    PERFORMANCE_METRIC = "performance_metric"       # Current performance metrics
    OPERATIONAL_TREND = "operational_trend"         # Short-term operational trends
    ANALYTICAL_CONTEXT = "analytical_context"       # Cross-session analytical context


class VietnameseMemoryDecisionAgent:
    """
    Vietnamese Memory Decision Agent for Intelligent Memory Layer Management
    
    This agent analyzes conversation content and makes intelligent decisions about:
    1. What information should be stored in long-term memory (business domain)
    2. What information should be stored in short-term memory (BI context)
    3. What should remain in in-session memory only
    4. When to migrate information between layers
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        context_manager: ContextManager = None,
        session_id: str = None,
        llm_config: Dict[str, Any] = None
    ):
        """
        Initialize Vietnamese Memory Decision Agent
        
        Args:
            memory_manager: Golett memory manager instance
            context_manager: Golett context manager instance
            session_id: Current session ID
            llm_config: LLM configuration for the agent
        """
        self.memory_manager = memory_manager
        self.context_manager = context_manager or ContextManager(memory_manager)
        self.session_id = session_id
        self.llm_config = llm_config
        
        # Create the CrewAI agent
        self.agent = self._create_agent()
        
        # Business domain keywords for Vietnamese (LONG-TERM - Strategic)
        self.business_domain_keywords = {
            BusinessDomainType.COMPANY_STATE: [
                "tình trạng công ty", "sức khỏe doanh nghiệp", "vị thế công ty",
                "trạng thái công ty", "tình hình tổng thể", "tổng quan công ty"
            ],
            BusinessDomainType.STRATEGIC_INSIGHT: [
                "chiến lược", "tầm nhìn", "định hướng", "kế hoạch dài hạn",
                "mục tiêu chiến lược", "phát triển bền vững", "strategic insight"
            ],
            BusinessDomainType.MARKET_ANALYSIS: [
                "thị trường", "cạnh tranh", "đối thủ", "xu hướng thị trường",
                "phân tích thị trường", "vị thế cạnh tranh", "industry analysis"
            ],
            BusinessDomainType.BUSINESS_RULE: [
                "quy định", "chính sách", "nguyên tắc kinh doanh",
                "quy tắc", "tiêu chuẩn", "compliance", "business rules"
            ],
            BusinessDomainType.DOMAIN_KNOWLEDGE: [
                "kiến thức ngành", "chuyên môn", "best practice",
                "kinh nghiệm", "know-how", "expertise", "domain knowledge"
            ],
            BusinessDomainType.INDUSTRY_KNOWLEDGE: [
                "kiến thức ngành", "industry knowledge", "ngành công nghiệp",
                "lĩnh vực kinh doanh", "sector knowledge"
            ],
            BusinessDomainType.COMPETITIVE_INTELLIGENCE: [
                "thông tin cạnh tranh", "competitive intelligence", "đối thủ cạnh tranh",
                "phân tích đối thủ", "competitor analysis"
            ]
        }
        
        # BI context keywords for Vietnamese (SHORT-TERM - Operational & BI)
        self.bi_context_keywords = {
            BIContextType.OPERATIONAL_INSIGHT: [
                "hiệu quả hoạt động", "kết quả hoạt động", "phân tích hoạt động",
                "operational performance", "current operations", "hoạt động hiện tại"
            ],
            BIContextType.TACTICAL_ANALYSIS: [
                "phân tích chiến thuật", "tactical analysis", "phân tích ngắn hạn",
                "immediate analysis", "current period analysis"
            ],
            BIContextType.DATA_DISCOVERY: [
                "khám phá dữ liệu", "tìm hiểu dữ liệu", "data exploration",
                "discovery", "data mining", "phát hiện dữ liệu"
            ],
            BIContextType.QUERY_PATTERN: [
                "pattern truy vấn", "thói quen query", "cách thức phân tích",
                "query preference", "analysis pattern", "user query patterns"
            ],
            BIContextType.BI_RESULT: [
                "kết quả BI", "BI analysis results", "báo cáo phân tích",
                "analysis results", "BI findings", "kết quả phân tích"
            ],
            BIContextType.PERFORMANCE_METRIC: [
                "chỉ số hiệu suất", "performance metrics", "KPI hiện tại",
                "current metrics", "operational metrics", "chỉ số hoạt động"
            ],
            BIContextType.OPERATIONAL_TREND: [
                "xu hướng hoạt động", "operational trends", "trend ngắn hạn",
                "current trends", "recent patterns", "xu hướng gần đây"
            ],
            BIContextType.ANALYTICAL_CONTEXT: [
                "context phân tích", "analytical context", "ngữ cảnh BI",
                "BI context", "analysis context", "phân tích context"
            ]
        }
        
        logger.info("✅ Vietnamese Memory Decision Agent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent for memory decisions"""
        
        agent_backstory = """
        Bạn là chuyên gia quản lý bộ nhớ thông minh cho hệ thống Business Intelligence tiếng Việt.
        
        NHIỆM VỤ CHÍNH:
        1. Phân tích nội dung hội thoại và quyết định lưu trữ bộ nhớ phù hợp
        2. Phân biệt giữa kiến thức miền kinh doanh (long-term) và ngữ cảnh BI (short-term)
        3. Đưa ra quyết định thông minh về việc di chuyển thông tin giữa các lớp bộ nhớ
        
        NGUYÊN TẮC QUYẾT ĐỊNH:
        
        🧠 LONG-TERM MEMORY (Bộ nhớ dài hạn):
        - Kiến thức về miền kinh doanh và ngành
        - Trạng thái và tình hình công ty
        - Insights chiến lược và xu hướng dài hạn
        - Quy tắc và chính sách kinh doanh
        - Patterns hoạt động quan trọng
        - Kiến thức có giá trị cross-session
        
        📝 SHORT-TERM MEMORY (Bộ nhớ ngắn hạn):
        - Ngữ cảnh BI quan trọng cho phiên làm việc
        - Insights chiến thuật và phát hiện tức thì
        - Preferences và patterns của user
        - Trạng thái workflow hiện tại
        - Kết quả phân tích session-specific
        - Context có thể hữu ích cho các câu hỏi tiếp theo
        
        🔄 IN-SESSION MEMORY (Bộ nhớ trong phiên):
        - Tin nhắn hội thoại hiện tại
        - Kết quả truy vấn tạm thời
        - Context làm việc tức thì
        - Thông tin chỉ cần thiết cho conversation hiện tại
        
        TIÊU CHÍ ĐÁNH GIÁ:
        - Tính bền vững của thông tin (persistent vs temporary)
        - Giá trị cross-session (có hữu ích cho sessions khác không?)
        - Tầm quan trọng kinh doanh (business impact)
        - Tính chất của insight (strategic vs tactical)
        - Khả năng tái sử dụng (reusability)
        """
        
        agent_goal = """
        Đưa ra quyết định thông minh và chính xác về việc lưu trữ thông tin trong các lớp bộ nhớ
        để tối ưu hóa hiệu quả của hệ thống BI và đảm bảo thông tin quan trọng được bảo tồn đúng cách.
        """
        
        return Agent(
            role="Vietnamese Memory Decision Specialist",
            goal=agent_goal,
            backstory=agent_backstory,
            verbose=True,
            allow_delegation=False,
            llm=self.llm_config
        )
    
    def analyze_and_decide_memory_storage(
        self,
        question: str,
        response: str,
        conversation_type: str,
        context_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze conversation and decide on memory storage strategy
        
        Args:
            question: User question
            response: Assistant response
            conversation_type: Type of conversation
            context_metadata: Additional context metadata
            
        Returns:
            Dictionary with memory decisions and reasoning
        """
        try:
            # Ensure we have valid inputs
            if not question:
                question = ""
            if not response:
                response = ""
            if not conversation_type:
                conversation_type = "conversational"
            
            # Analyze content for business domain knowledge
            try:
                business_domain_analysis = self._analyze_business_domain_content(question, response)
                if business_domain_analysis is None:
                    business_domain_analysis = {"has_business_domain_content": False, "overall_importance": 0.0}
            except Exception as e:
                logger.error(f"Error in business domain analysis: {e}")
                business_domain_analysis = {"has_business_domain_content": False, "overall_importance": 0.0}
            
            # Analyze content for BI context importance
            try:
                bi_context_analysis = self._analyze_bi_context_importance(question, response, conversation_type)
                if bi_context_analysis is None:
                    bi_context_analysis = {"has_bi_context": False, "overall_bi_importance": 0.0}
            except Exception as e:
                logger.error(f"Error in BI context analysis: {e}")
                bi_context_analysis = {"has_bi_context": False, "overall_bi_importance": 0.0}
            
            # Analyze content for operational system states
            try:
                operational_state_analysis = self._analyze_operational_state_content(question, response, context_metadata or {})
                if operational_state_analysis is None:
                    operational_state_analysis = {"should_store_in_session": False}
            except Exception as e:
                logger.error(f"Error in operational state analysis: {e}")
                operational_state_analysis = {"should_store_in_session": False}
            
            # Determine storage decisions
            try:
                storage_decisions = self._determine_storage_decisions(
                    business_domain_analysis,
                    bi_context_analysis,
                    operational_state_analysis,
                    conversation_type,
                    context_metadata or {},
                    question,
                    response
                )
                if storage_decisions is None:
                    storage_decisions = {"store_in_long_term": False, "store_in_short_term": False, "store_in_session_only": True}
            except Exception as e:
                logger.error(f"Error in storage decisions: {e}")
                storage_decisions = {"store_in_long_term": False, "store_in_short_term": False, "store_in_session_only": True}
            
            # Generate reasoning
            try:
                reasoning = self._generate_decision_reasoning(
                    business_domain_analysis,
                    bi_context_analysis,
                    operational_state_analysis,
                    storage_decisions
                )
                if reasoning is None:
                    reasoning = "Analysis completed with fallback reasoning"
            except Exception as e:
                logger.error(f"Error in reasoning generation: {e}")
                reasoning = f"Analysis completed with error in reasoning: {str(e)}"
            
            return {
                "storage_decisions": storage_decisions,
                "business_domain_analysis": business_domain_analysis,
                "bi_context_analysis": bi_context_analysis,
                "operational_state_analysis": operational_state_analysis,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat(),
                "agent": "VietnameseMemoryDecisionAgent"
            }
            
        except Exception as e:
            logger.error(f"Error in memory decision analysis: {e}")
            return self._get_fallback_decision(conversation_type)
    
    def _analyze_business_domain_content(self, question: str, response: str) -> Dict[str, Any]:
        """Analyze content for business domain knowledge indicators"""
        
        combined_text = f"{question} {response}".lower()
        
        domain_scores = {}
        detected_domains = []
        
        for domain_type, keywords in self.business_domain_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                domain_scores[domain_type.value] = {
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "relevance": min(score / len(keywords), 1.0)
                }
                detected_domains.append(domain_type.value)
        
        # Calculate overall business domain importance
        total_score = sum(info["score"] for info in domain_scores.values())
        max_possible_score = sum(len(keywords) for keywords in self.business_domain_keywords.values())
        overall_importance = min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        
        # Determine if this contains strategic vs operational knowledge
        strategic_domains = [
            BusinessDomainType.STRATEGIC_INSIGHT.value,
            BusinessDomainType.MARKET_ANALYSIS.value,
            BusinessDomainType.COMPANY_STATE.value
        ]
        
        operational_domains = [
            BusinessDomainType.BUSINESS_RULE.value,
            BusinessDomainType.DOMAIN_KNOWLEDGE.value
        ]
        
        is_strategic = any(domain in detected_domains for domain in strategic_domains)
        is_operational = any(domain in detected_domains for domain in operational_domains)
        
        return {
            "domain_scores": domain_scores,
            "detected_domains": detected_domains,
            "overall_importance": overall_importance,
            "is_strategic": is_strategic,
            "is_operational": is_operational,
            "has_business_domain_content": len(detected_domains) > 0,
            "primary_domain": max(domain_scores.keys(), key=lambda k: domain_scores[k]["score"]) if domain_scores else None
        }
    
    def _analyze_bi_context_importance(self, question: str, response: str, conversation_type: str) -> Dict[str, Any]:
        """Analyze content for BI context importance"""
        
        combined_text = f"{question} {response}".lower()
        
        context_scores = {}
        detected_contexts = []
        
        for context_type, keywords in self.bi_context_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                context_scores[context_type.value] = {
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "relevance": min(score / len(keywords), 1.0)
                }
                detected_contexts.append(context_type.value)
        
        # Calculate BI context importance based on conversation type
        conversation_type_weights = {
            "data_analysis": 0.8,
            "follow_up": 0.6,
            "explanation": 0.5,
            "conversational": 0.2
        }
        
        base_importance = conversation_type_weights.get(conversation_type, 0.3)
        
        # Boost importance if contains specific BI indicators
        bi_indicators = [
            "phân tích", "dữ liệu", "báo cáo", "thống kê", "truy vấn",
            "dashboard", "metric", "KPI", "insight", "trend"
        ]
        
        bi_indicator_count = sum(1 for indicator in bi_indicators if indicator in combined_text)
        bi_boost = min(bi_indicator_count * 0.1, 0.3)
        
        overall_bi_importance = min(base_importance + bi_boost, 1.0)
        
        # Determine if this is session-specific or has broader value
        session_specific_indicators = ["hiện tại", "lúc này", "session này", "phiên này"]
        broader_value_indicators = ["xu hướng", "pattern", "thường xuyên", "luôn luôn"]
        
        is_session_specific = any(indicator in combined_text for indicator in session_specific_indicators)
        has_broader_value = any(indicator in combined_text for indicator in broader_value_indicators)
        
        return {
            "context_scores": context_scores,
            "detected_contexts": detected_contexts,
            "overall_bi_importance": overall_bi_importance,
            "conversation_type_weight": base_importance,
            "bi_indicator_boost": bi_boost,
            "is_session_specific": is_session_specific,
            "has_broader_value": has_broader_value,
            "has_bi_context": len(detected_contexts) > 0 or bi_indicator_count > 0,
            "primary_context": max(context_scores.keys(), key=lambda k: context_scores[k]["score"]) if context_scores else None
        }
    
    def _analyze_operational_state_content(self, question: str, response: str, context_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for system noise vs valuable operational business content"""
        
        # SEPARATE CONTENT FROM METADATA ANALYSIS
        # Only analyze the actual question and response content, not metadata
        combined_content = f"{question} {response}".lower()
        metadata_str = str(context_metadata).lower() if context_metadata else ""
        
        # SYSTEM NOISE DETECTION (should go to IN_SESSION only)
        # Focus on ACTUAL system noise in content, not metadata
        system_noise_indicators = [
            "crew_config", "agent_config", "workflow_state", "system_setup",
            "crew_creation", "agent_initialization", "system_configuration",
            "crew_registration", "agent_registration", "backend_config",
            "postgres_connection", "qdrant_url", "api_token", "config_setup"
        ]
        
        # REFINED system noise patterns - focus on actual system operations, not business terms
        system_noise_patterns = [
            # Technical system operations (not business operations)
            "crew_id", "agent_count", "task_count", "registered_at",
            "auto_created", "last_activity", "backend", "adapter",
            
            # Memory system technical metadata (not business memory)
            "memory_layer", "context_type", "context_subtype", "chunk_count",
            "collection_name", "source_file", "chunk_size", "overlap_size",
            
            # Technical configuration (not business configuration)
            "postgres_connection", "qdrant_url", "api_url", "api_token",
            "initialization", "setup", "backend", "adapter", "config"
        ]
        
        # VALUABLE AGENT OUTPUT DETECTION (should be considered for SHORT_TERM)
        valuable_agent_output_indicators = [
            # Vietnamese business analysis outputs
            "phân tích dữ liệu kinh doanh", "insights và nhận định", "khuyến nghị",
            "kết quả phân tích", "báo cáo chi tiết", "thống kê quan trọng",
            "xu hướng kinh doanh", "hiệu quả hoạt động", "kết quả kinh doanh",
            
            # English business analysis outputs
            "business analysis", "data insights", "recommendations", "findings",
            "business intelligence", "performance analysis", "operational insights",
            "data analysis results", "business metrics", "KPI analysis",
            
            # Structured analysis outputs
            "📊", "💡", "📈", "📋", "🔍", "📝",  # Analysis emojis
            "phân tích:", "insights:", "khuyến nghị:", "kết quả:",
            "analysis:", "findings:", "recommendations:", "summary:"
        ]
        
        # ENHANCED OPERATIONAL BUSINESS CONTENT (should be considered for SHORT_TERM)
        operational_business_indicators = [
            # Current business performance
            "hiệu quả hoạt động", "kết quả kinh doanh", "performance hiện tại",
            "operational performance", "current operations", "business results",
            
            # Metrics and KPIs
            "chỉ số KPI", "metrics hiện tại", "performance metrics", "operational metrics",
            "chỉ số hoạt động", "đo lường hiệu quả", "business metrics",
            
            # Data analysis and insights
            "phân tích dữ liệu", "data analysis", "business intelligence",
            "BI insights", "analytical findings", "data-driven insights",
            
            # Business reporting and summaries
            "báo cáo kinh doanh", "business report", "executive summary",
            "operational summary", "performance report", "business overview"
        ]
        
        # CHECK FOR ACTUAL SYSTEM NOISE (only in content, not metadata)
        system_noise_score = 0
        detected_noise_patterns = []
        
        for pattern in system_noise_patterns:
            if pattern in combined_content:  # Only check content, not metadata
                system_noise_score += 1
                detected_noise_patterns.append(pattern)
        
        # Check for system noise indicators in content only
        is_system_noise = False
        detected_system_states = []
        
        for indicator in system_noise_indicators:
            if indicator in combined_content:  # Only check content, not metadata
                is_system_noise = True
                detected_system_states.append(indicator)
        
        # CHECK FOR VALUABLE AGENT OUTPUTS
        valuable_output_score = 0
        detected_valuable_outputs = []
        
        for indicator in valuable_agent_output_indicators:
            if indicator in combined_content:
                valuable_output_score += 1
                detected_valuable_outputs.append(indicator)
        
        # CHECK FOR OPERATIONAL BUSINESS CONTENT
        operational_business_score = 0
        detected_business_operations = []
        
        for indicator in operational_business_indicators:
            if indicator in combined_content:
                operational_business_score += 1
                detected_business_operations.append(indicator)
        
        # Additional business operational content detection
        business_operational_patterns = [
            # Performance and efficiency
            "hiệu suất", "năng suất", "efficiency", "productivity", "performance",
            
            # Current business metrics
            "doanh thu", "lợi nhuận", "revenue", "profit", "sales",
            "financial performance", "operational results",
            
            # Business insights and analysis
            "insight", "phát hiện", "nhận định", "kết luận", "đánh giá",
            "analysis", "assessment", "evaluation", "conclusion"
        ]
        
        business_pattern_matches = sum(1 for pattern in business_operational_patterns 
                                     if pattern in combined_content)
        
        # IMPROVED DECISION LOGIC
        # System noise should go to IN_SESSION only - but be much more conservative
        is_pure_system_noise = (
            system_noise_score >= 5 or  # Much higher threshold - need many system patterns
            (is_system_noise and system_noise_score >= 3)  # System indicators + multiple patterns
        )
        
        # Valuable content should be considered for SHORT_TERM - much more liberal
        has_valuable_content = (
            valuable_output_score >= 1 or      # Any valuable agent output indicator
            operational_business_score >= 1 or  # Any business operational indicator
            business_pattern_matches >= 2 or    # Multiple business patterns
            (operational_business_score >= 1 and business_pattern_matches >= 1)  # Combined indicators
        )
        
        # PRIORITIZE VALUABLE CONTENT OVER SYSTEM NOISE
        # If content has value, don't classify as system noise even if some noise patterns exist
        should_store_in_session_only = is_pure_system_noise and not has_valuable_content
        
        # METADATA-ONLY SYSTEM NOISE CHECK
        # Check if system noise is only in metadata, not content
        metadata_only_noise = False
        if context_metadata:
            metadata_noise_score = 0
            for pattern in system_noise_patterns:
                if pattern in metadata_str and pattern not in combined_content:
                    metadata_noise_score += 1
            metadata_only_noise = metadata_noise_score >= 3
        
        return {
            # System noise detection
            "is_system_noise": is_pure_system_noise,
            "metadata_only_noise": metadata_only_noise,
            "detected_system_states": detected_system_states,
            "detected_noise_patterns": detected_noise_patterns,
            "system_noise_score": system_noise_score,
            
            # Valuable content detection
            "has_valuable_content": has_valuable_content,
            "valuable_output_score": valuable_output_score,
            "detected_valuable_outputs": detected_valuable_outputs,
            
            # Operational business content detection
            "has_valuable_operational_content": has_valuable_content,  # Simplified
            "detected_business_operations": detected_business_operations,
            "operational_business_score": operational_business_score,
            "business_pattern_matches": business_pattern_matches,
            
            # Final decision
            "should_store_in_session": should_store_in_session_only,
            "content_type": self._determine_operational_content_type(
                is_pure_system_noise, has_valuable_content
            ),
            "noise_reason": self._get_noise_reason(
                is_pure_system_noise, False, system_noise_score, 
                0, detected_noise_patterns
            ) if is_pure_system_noise else None,
            
            # Additional context
            "content_analysis_summary": {
                "total_valuable_indicators": valuable_output_score + operational_business_score,
                "total_noise_indicators": system_noise_score,
                "has_business_analysis_structure": valuable_output_score >= 2,
                "recommendation": "SHORT_TERM" if has_valuable_content else ("IN_SESSION" if is_pure_system_noise else "EVALUATE_FURTHER")
            }
        }
    
    def _get_noise_reason(self, is_system_noise: bool, has_system_config: bool, 
                         system_noise_score: int, json_system_score: int, 
                         detected_patterns: List[str]) -> str:
        """Generate a reason for why content is considered system noise"""
        reasons = []
        
        if is_system_noise:
            reasons.append("System noise detected")
        if has_system_config:
            reasons.append("System configuration data")
        if system_noise_score >= 3:
            reasons.append(f"High system noise score ({system_noise_score})")
        if json_system_score >= 2:
            reasons.append(f"JSON system data detected ({json_system_score})")
        if detected_patterns:
            top_patterns = detected_patterns[:3]  # Show top 3 patterns
            reasons.append(f"Patterns: {', '.join(top_patterns)}")
        
        return " | ".join(reasons) if reasons else "System operational state"
    
    def _determine_operational_content_type(self, is_pure_system_noise: bool, has_valuable_content: bool) -> str:
        """Determine the type of operational content"""
        if is_pure_system_noise and not has_valuable_content:
            return "system_noise"
        elif has_valuable_content and not is_pure_system_noise:
            return "valuable_business_operational"
        elif has_valuable_content and is_pure_system_noise:
            return "mixed_content"  # Contains both system noise and valuable content
        else:
            return "neutral_content"
    
    def _determine_storage_decisions(
        self,
        business_domain_analysis: Dict[str, Any],
        bi_context_analysis: Dict[str, Any],
        operational_state_analysis: Dict[str, Any],
        conversation_type: str,
        context_metadata: Dict[str, Any],
        question: str = "",
        response: str = ""
    ) -> Dict[str, Any]:
        """Determine storage decisions based on STRICT analysis with mandatory summarization"""
        
        decisions = {
            "store_in_long_term": False,
            "store_in_short_term": False,
            "store_in_session_only": False,
            "long_term_content": None,
            "short_term_content": None,
            "long_term_importance": 0.0,
            "short_term_importance": 0.0,
            "migration_recommendations": [],
            "requires_summarization": False,
            "summary_type": None
        }
        
        # Check if this is operational system state (should go to IN_SESSION only)
        if operational_state_analysis.get("should_store_in_session", False):
            decisions["store_in_session_only"] = True
            decisions["session_reason"] = "Operational system state - belongs in IN_SESSION memory"
            return decisions
        
        # STRICT Long-term storage decision (Strategic Business Knowledge ONLY)
        business_importance = business_domain_analysis.get("overall_importance", 0.0)
        is_strategic = business_domain_analysis.get("is_strategic", False)
        has_business_content = business_domain_analysis.get("has_business_domain_content", False)
        detected_domains = business_domain_analysis.get("detected_domains", [])
        
        # MUCH STRICTER long-term thresholds
        long_term_threshold = 0.7  # Raised from 0.3 to 0.7
        strategic_threshold = 0.6   # Raised from 0.2 to 0.6
        
        # Additional strict criteria for long-term storage
        has_multiple_domains = len(detected_domains) >= 2  # Must have multiple business domains
        has_strategic_keywords = self._has_strategic_business_keywords(f"{question} {response}")
        
        # STRICT: Must meet ALL criteria for long-term storage
        meets_long_term_criteria = (
            business_importance >= long_term_threshold and
            has_business_content and
            (is_strategic or has_strategic_keywords) and
            has_multiple_domains
        )
        
        # Alternative: Strategic content with very high importance
        meets_strategic_criteria = (
            is_strategic and 
            business_importance >= strategic_threshold and
            has_strategic_keywords
        )
        
        if meets_long_term_criteria or meets_strategic_criteria:
            decisions["store_in_long_term"] = True
            decisions["long_term_importance"] = min(0.8 + business_importance * 0.2, 1.0)
            decisions["requires_summarization"] = True
            decisions["summary_type"] = "strategic_business_insight"
            decisions["long_term_content"] = {
                "type": "strategic_business_knowledge",
                "primary_domain": business_domain_analysis.get("primary_domain"),
                "is_strategic": is_strategic,
                "detected_domains": detected_domains,
                "requires_insight_extraction": True
            }
        
        # STRICT Short-term storage decision (BI Context & Operational Business Insights)
        bi_importance = bi_context_analysis.get("overall_bi_importance", 0.0)
        has_bi_content = bi_context_analysis.get("has_bi_context", False)
        has_broader_value = bi_context_analysis.get("has_broader_value", False)
        detected_contexts = bi_context_analysis.get("detected_contexts", [])
        
        # NEW: Consider valuable operational business content
        has_valuable_operational = operational_state_analysis.get("has_valuable_operational_content", False)
        has_valuable_content = operational_state_analysis.get("has_valuable_content", False)
        valuable_output_score = operational_state_analysis.get("valuable_output_score", 0)
        
        # ENHANCED: More liberal SHORT_TERM storage criteria
        # Traditional BI context criteria (existing)
        bi_threshold = 0.4  # Reduced from 0.5 to 0.4
        meets_bi_criteria = (
            bi_importance >= bi_threshold and
            has_bi_content and
            (has_broader_value or len(detected_contexts) >= 1)
        )
        
        # NEW: Valuable agent output criteria (very liberal)
        meets_agent_output_criteria = (
            valuable_output_score >= 1 or  # Any valuable output indicator
            has_valuable_content
        )
        
        # NEW: Operational business content criteria (liberal)
        operational_score = operational_state_analysis.get("operational_business_score", 0)
        meets_operational_criteria = (
            has_valuable_operational and
            operational_score >= 1  # Any business operational indicator
        )
        
        # NEW: Business relevance criteria (liberal)
        has_quantitative_data = self._has_quantitative_business_data(f"{question} {response}")
        has_actionable_insights = self._has_actionable_business_insights(f"{question} {response}")
        meets_business_relevance = (
            has_quantitative_data or
            has_actionable_insights or
            (bi_importance >= 0.3 and len(detected_contexts) >= 1)  # Lower threshold with context
        )
        
        # DECISION: Store in SHORT_TERM if ANY criteria is met (much more liberal)
        if meets_agent_output_criteria or meets_bi_criteria or meets_operational_criteria or meets_business_relevance:
            decisions["store_in_short_term"] = True
            decisions["short_term_importance"] = min(0.5 + bi_importance * 0.3 + valuable_output_score * 0.1, 1.0)
            decisions["short_term_content"] = {
                "type": "bi_operational_context",
                "primary_context": bi_context_analysis.get("primary_context"),
                "has_broader_value": has_broader_value,
                "detected_contexts": detected_contexts,
                "has_quantitative_data": has_quantitative_data,
                "has_actionable_insights": has_actionable_insights,
                "has_valuable_operational_content": has_valuable_operational,
                "valuable_output_score": valuable_output_score,
                "pathway_used": self._determine_storage_pathway(
                    meets_bi_criteria, meets_agent_output_criteria, 
                    meets_operational_criteria, meets_business_relevance
                )
            }
        
        # Migration recommendations (more liberal)
        if decisions["store_in_short_term"] and business_importance > 0.7:  # Reduced from 0.8 to 0.7
            decisions["migration_recommendations"].append({
                "type": "consider_long_term_migration",
                "reason": "High strategic business importance detected in operational content",
                "threshold_met": business_importance
            })
        
        # If nothing meets criteria, store only in session (but this should be rare now)
        if not decisions["store_in_long_term"] and not decisions["store_in_short_term"]:
            decisions["store_in_session_only"] = True
            decisions["session_reason"] = "Content does not contain business-relevant information for cross-session storage"
        
        return decisions
    
    def _determine_storage_pathway(self, meets_bi: bool, meets_agent: bool, meets_operational: bool, meets_business: bool) -> str:
        """Determine which pathway was used for SHORT_TERM storage decision"""
        if meets_agent:
            return "valuable_agent_output"
        elif meets_bi:
            return "traditional_bi_context"
        elif meets_operational:
            return "operational_business_content"
        elif meets_business:
            return "business_relevance"
        else:
            return "unknown"
    
    def _has_strategic_business_keywords(self, text: str) -> bool:
        """Check for strategic business keywords that indicate long-term value"""
        strategic_keywords = [
            "chiến lược dài hạn", "tầm nhìn công ty", "định hướng phát triển",
            "mục tiêu chiến lược", "kế hoạch tổng thể", "strategic planning",
            "long-term strategy", "business strategy", "competitive advantage",
            "market position", "industry analysis", "business transformation"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in strategic_keywords)
    
    def _has_quantitative_business_data(self, text: str) -> bool:
        """Check for quantitative business data that adds value"""
        import re
        
        # Look for numbers with business context
        number_patterns = [
            r'\d+%',  # Percentages
            r'\d+\s*(triệu|tỷ|nghìn|million|billion|thousand)',  # Large numbers
            r'\d+\s*(VND|USD|EUR)',  # Currency
            r'\d+\.\d+',  # Decimals
            r'\d+\s*(tăng|giảm|increase|decrease)',  # Growth/decline
        ]
        
        for pattern in number_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _has_actionable_business_insights(self, text: str) -> bool:
        """Check for actionable business insights"""
        actionable_keywords = [
            "nên", "khuyến nghị", "đề xuất", "cần thiết", "should", "recommend",
            "suggest", "propose", "action", "next steps", "improvement",
            "optimization", "strategy", "solution", "approach"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in actionable_keywords)
    
    def _generate_decision_reasoning(
        self,
        business_domain_analysis: Dict[str, Any],
        bi_context_analysis: Dict[str, Any],
        operational_state_analysis: Dict[str, Any],
        storage_decisions: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for the decisions"""
        
        # Ensure all analysis dictionaries are not None
        if business_domain_analysis is None:
            business_domain_analysis = {"has_business_domain_content": False, "overall_importance": 0.0}
        if bi_context_analysis is None:
            bi_context_analysis = {"has_bi_context": False, "overall_bi_importance": 0.0}
        if operational_state_analysis is None:
            operational_state_analysis = {"should_store_in_session": False}
        if storage_decisions is None:
            storage_decisions = {"store_in_long_term": False, "store_in_short_term": False, "store_in_session_only": True}
        
        reasoning_parts = []
        
        # Operational state reasoning (IN_SESSION)
        if operational_state_analysis.get("should_store_in_session"):
            states = operational_state_analysis.get("detected_system_states", [])
            content_type = operational_state_analysis.get("content_type", "unknown")
            noise_reason = operational_state_analysis.get("noise_reason")
            
            reasoning_parts.append(f"🔧 Phát hiện nội dung hệ thống:")
            reasoning_parts.append(f"   - Loại nội dung: {content_type}")
            if states:
                reasoning_parts.append(f"   - Các trạng thái hệ thống: {', '.join(states)}")
            if noise_reason:
                reasoning_parts.append(f"   - Lý do: {noise_reason}")
            reasoning_parts.append(f"   - Quyết định: Lưu vào IN_SESSION memory (chỉ cho phiên hiện tại)")
            return "\n".join(reasoning_parts)
        
        # Check for valuable operational business content that should be considered for SHORT_TERM
        has_valuable_operational = operational_state_analysis.get("has_valuable_operational_content", False)
        has_valuable_content = operational_state_analysis.get("has_valuable_content", False)
        valuable_output_score = operational_state_analysis.get("valuable_output_score", 0)
        
        if has_valuable_content or valuable_output_score > 0:
            business_operations = operational_state_analysis.get("detected_business_operations", [])
            valuable_outputs = operational_state_analysis.get("detected_valuable_outputs", [])
            operational_score = operational_state_analysis.get("operational_business_score", 0)
            
            reasoning_parts.append(f"💡 Phát hiện nội dung có giá trị từ agent:")
            reasoning_parts.append(f"   - Điểm số valuable output: {valuable_output_score}")
            reasoning_parts.append(f"   - Điểm số hoạt động kinh doanh: {operational_score}")
            if valuable_outputs:
                reasoning_parts.append(f"   - Các chỉ báo có giá trị: {', '.join(valuable_outputs[:3])}")  # Show top 3
            if business_operations:
                reasoning_parts.append(f"   - Các hoạt động kinh doanh: {', '.join(business_operations[:3])}")  # Show top 3
            reasoning_parts.append(f"   - Đánh giá: Phù hợp cho SHORT-TERM memory")
        elif has_valuable_operational:
            business_operations = operational_state_analysis.get("detected_business_operations", [])
            operational_score = operational_state_analysis.get("operational_business_score", 0)
            reasoning_parts.append(f"⚙️ Phát hiện nội dung hoạt động kinh doanh có giá trị:")
            reasoning_parts.append(f"   - Điểm số hoạt động: {operational_score}")
            if business_operations:
                reasoning_parts.append(f"   - Các chỉ số: {', '.join(business_operations[:3])}")  # Show top 3
            reasoning_parts.append(f"   - Đánh giá: Có thể phù hợp cho SHORT-TERM memory")
        
        # Business domain reasoning (LONG_TERM)
        if business_domain_analysis.get("has_business_domain_content"):
            domains = business_domain_analysis.get("detected_domains", [])
            importance = business_domain_analysis.get("overall_importance", 0.0)
            is_strategic = business_domain_analysis.get("is_strategic", False)
            
            reasoning_parts.append(f"🏢 Phát hiện kiến thức miền kinh doanh chiến lược:")
            reasoning_parts.append(f"   - Các miền: {', '.join(domains)}")
            reasoning_parts.append(f"   - Tầm quan trọng: {importance:.2f}")
            reasoning_parts.append(f"   - Tính chiến lược: {'Có' if is_strategic else 'Không'}")
        
        # BI context reasoning (SHORT_TERM)
        if bi_context_analysis.get("has_bi_context"):
            contexts = bi_context_analysis.get("detected_contexts", [])
            importance = bi_context_analysis.get("overall_bi_importance", 0.0)
            broader_value = bi_context_analysis.get("has_broader_value", False)
            
            reasoning_parts.append(f"📊 Phát hiện ngữ cảnh BI và insights hoạt động:")
            reasoning_parts.append(f"   - Các ngữ cảnh: {', '.join(contexts)}")
            reasoning_parts.append(f"   - Tầm quan trọng BI: {importance:.2f}")
            reasoning_parts.append(f"   - Giá trị cross-session: {'Có' if broader_value else 'Không'}")
        
        # Storage decisions reasoning
        reasoning_parts.append(f"💾 Quyết định lưu trữ:")
        
        if storage_decisions.get("store_in_long_term"):
            lt_importance = storage_decisions.get("long_term_importance", 0.0)
            reasoning_parts.append(f"   ✅ LONG-TERM: Có (Importance: {lt_importance:.2f})")
            reasoning_parts.append(f"      Lý do: Chứa kiến thức miền kinh doanh chiến lược có giá trị dài hạn")
        else:
            reasoning_parts.append(f"   ❌ LONG-TERM: Không - Không đủ tính chiến lược hoặc tầm quan trọng")
        
        if storage_decisions.get("store_in_short_term"):
            st_importance = storage_decisions.get("short_term_importance", 0.0)
            short_term_content = storage_decisions.get("short_term_content", {})
            pathway_used = short_term_content.get("pathway_used", "unknown")
            
            reasoning_parts.append(f"   ✅ SHORT-TERM: Có (Importance: {st_importance:.2f})")
            
            # Show the pathway used for the decision
            pathway_descriptions = {
                "valuable_agent_output": "Phát hiện output có giá trị từ agent",
                "traditional_bi_context": "Ngữ cảnh BI truyền thống",
                "operational_business_content": "Nội dung hoạt động kinh doanh",
                "business_relevance": "Liên quan đến kinh doanh"
            }
            
            pathway_desc = pathway_descriptions.get(pathway_used, pathway_used)
            reasoning_parts.append(f"      Pathway: {pathway_desc}")
            reasoning_parts.append(f"      Lý do: Chứa nội dung có giá trị cho cross-session context")
        else:
            reasoning_parts.append(f"   ❌ SHORT-TERM: Không - Không chứa nội dung có giá trị cho cross-session storage")
        
        if storage_decisions.get("store_in_session_only"):
            reasoning_parts.append(f"   ✅ IN-SESSION: Có")
            reasoning_parts.append(f"      Lý do: {storage_decisions.get('session_reason', 'Chỉ cần thiết cho phiên hiện tại')}")
        
        # Migration recommendations
        migrations = storage_decisions.get("migration_recommendations", [])
        if migrations:
            reasoning_parts.append(f"🔄 Khuyến nghị:")
            for migration in migrations:
                if isinstance(migration, dict):
                    reasoning_parts.append(f"   - {migration.get('reason', 'Unknown recommendation')}")
        
        return "\n".join(reasoning_parts)
    
    def _get_fallback_decision(self, conversation_type: str) -> Dict[str, Any]:
        """Get fallback decision when analysis fails"""
        
        # Simple fallback based on conversation type
        fallback_decisions = {
            "data_analysis": {
                "store_in_long_term": False,
                "store_in_short_term": True,
                "short_term_importance": 0.6
            },
            "follow_up": {
                "store_in_long_term": False,
                "store_in_short_term": True,
                "short_term_importance": 0.5
            },
            "explanation": {
                "store_in_long_term": False,
                "store_in_short_term": False
            },
            "conversational": {
                "store_in_long_term": False,
                "store_in_short_term": False
            }
        }
        
        base_decision = fallback_decisions.get(conversation_type, {
            "store_in_long_term": False,
            "store_in_short_term": False
        })
        
        return {
            "storage_decisions": base_decision,
            "business_domain_analysis": {"has_business_domain_content": False},
            "bi_context_analysis": {"has_bi_context": False},
            "operational_state_analysis": {"should_store_in_session": False},
            "reasoning": f"Fallback decision for conversation type: {conversation_type}",
            "timestamp": datetime.now().isoformat(),
            "agent": "VietnameseMemoryDecisionAgent",
            "fallback": True
        }
    
    def create_memory_decision_task(
        self,
        question: str,
        response: str,
        conversation_type: str,
        context_metadata: Dict[str, Any] = None
    ) -> Task:
        """Create a CrewAI task for memory decision making"""
        
        task_description = f"""
        Phân tích cuộc hội thoại sau và đưa ra quyết định thông minh về việc lưu trữ bộ nhớ:
        
        THÔNG TIN CUỘC HỘI THOẠI:
        - Loại hội thoại: {conversation_type}
        - Câu hỏi: {question[:200]}...
        - Trả lời: {response[:300]}...
        
        YÊU CẦU PHÂN TÍCH:
        1. Xác định nội dung kiến thức miền kinh doanh (business domain knowledge)
        2. Đánh giá tầm quan trọng ngữ cảnh BI (BI context importance)
        3. Quyết định lưu trữ long-term vs short-term memory
        4. Đưa ra lý do chi tiết cho quyết định
        
        KẾT QUẢ MONG MUỐN:
        - Quyết định có lưu vào long-term memory không (và tại sao)
        - Quyết định có lưu vào short-term memory không (và tại sao)
        - Mức độ quan trọng cho mỗi lớp bộ nhớ
        - Lý do chi tiết cho từng quyết định
        - Khuyến nghị di chuyển (nếu có)
        
        Hãy phân tích kỹ lưỡng và đưa ra quyết định chính xác dựa trên nguyên tắc đã được đào tạo.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="Detailed memory storage decision with reasoning in Vietnamese"
        )
    
    def execute_memory_decisions(
        self,
        question: str,
        response: str,
        memory_decisions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the memory storage decisions with MANDATORY SUMMARIZATION"""
        
        execution_results = {
            "long_term_stored": False,
            "short_term_stored": False,
            "long_term_id": None,
            "short_term_id": None,
            "summary_created": False,
            "insight_created": False,
            "errors": []
        }
        
        try:
            storage_decisions = memory_decisions.get("storage_decisions", {})
            requires_summarization = storage_decisions.get("requires_summarization", False)
            
            # Execute long-term storage with MANDATORY insight extraction
            if storage_decisions.get("store_in_long_term"):
                try:
                    long_term_content = storage_decisions.get("long_term_content", {})
                    importance = storage_decisions.get("long_term_importance", 0.8)
                    
                    # MANDATORY: Create strategic business insight (not raw content)
                    strategic_insight = self._create_strategic_business_insight(
                        question, response, long_term_content
                    )
                    
                    # Only store if insight is substantial (minimum length check)
                    if len(strategic_insight) < 50:
                        execution_results["errors"].append("Strategic insight too short - not stored")
                        return execution_results
                    
                    long_term_id = self.memory_manager.store_context(
                        session_id=self.session_id,
                        context_type="strategic_business_insight",
                        data=strategic_insight,
                        importance=importance,
                        metadata={
                            "insight_type": "strategic_business",
                            "primary_domain": long_term_content.get("primary_domain"),
                            "is_strategic": long_term_content.get("is_strategic", False),
                            "detected_domains": long_term_content.get("detected_domains", []),
                            "agent_decision": "VietnameseMemoryDecisionAgent",
                            "timestamp": datetime.now().isoformat(),
                            "cross_session_value": True,
                            "content_type": "summarized_insight",
                            "original_length": len(question + response),
                            "summary_length": len(strategic_insight),
                            "compression_ratio": len(strategic_insight) / len(question + response)
                        },
                        memory_layer=MemoryLayer.LONG_TERM
                    )
                    
                    execution_results["long_term_stored"] = True
                    execution_results["long_term_id"] = long_term_id
                    execution_results["insight_created"] = True
                    
                except Exception as e:
                    execution_results["errors"].append(f"Long-term insight creation error: {str(e)}")
            
            # Execute short-term storage with MANDATORY summarization
            if storage_decisions.get("store_in_short_term"):
                try:
                    short_term_content = storage_decisions.get("short_term_content", {})
                    importance = storage_decisions.get("short_term_importance", 0.6)
                    
                    # MANDATORY: Create BI operational summary (not raw content)
                    bi_summary = self._create_bi_operational_summary(
                        question, response, short_term_content
                    )
                    
                    # Only store if summary is substantial (minimum length check)
                    if len(bi_summary) < 30:
                        execution_results["errors"].append("BI summary too short - not stored")
                        return execution_results
                    
                    short_term_id = self.memory_manager.store_context(
                        session_id=self.session_id,
                        context_type="bi_operational_summary",
                        data=bi_summary,
                        importance=importance,
                        metadata={
                            "summary_type": "bi_operational",
                            "primary_context": short_term_content.get("primary_context"),
                            "has_broader_value": short_term_content.get("has_broader_value", False),
                            "detected_contexts": short_term_content.get("detected_contexts", []),
                            "has_quantitative_data": short_term_content.get("has_quantitative_data", False),
                            "has_actionable_insights": short_term_content.get("has_actionable_insights", False),
                            "agent_decision": "VietnameseMemoryDecisionAgent",
                            "timestamp": datetime.now().isoformat(),
                            "content_type": "summarized_context",
                            "original_length": len(question + response),
                            "summary_length": len(bi_summary),
                            "compression_ratio": len(bi_summary) / len(question + response)
                        },
                        memory_layer=MemoryLayer.SHORT_TERM
                    )
                    
                    execution_results["short_term_stored"] = True
                    execution_results["short_term_id"] = short_term_id
                    execution_results["summary_created"] = True
                    
                except Exception as e:
                    execution_results["errors"].append(f"Short-term summary creation error: {str(e)}")
            
            return execution_results
            
        except Exception as e:
            execution_results["errors"].append(f"General execution error: {str(e)}")
            return execution_results
    
    def _create_strategic_business_insight(
        self,
        question: str,
        response: str,
        content_info: Dict[str, Any]
    ) -> str:
        """Create a strategic business insight for long-term storage (SUMMARIZED)"""
        
        primary_domain = content_info.get("primary_domain", "unknown")
        is_strategic = content_info.get("is_strategic", False)
        detected_domains = content_info.get("detected_domains", [])
        
        # Extract key strategic insights from the response
        strategic_elements = self._extract_strategic_elements(response)
        business_implications = self._extract_business_implications(response)
        
        # Create a concise strategic insight (NOT raw content)
        insight_parts = []
        
        if is_strategic:
            insight_parts.append(f"🎯 STRATEGIC INSIGHT ({primary_domain}):")
        else:
            insight_parts.append(f"🏢 BUSINESS DOMAIN INSIGHT ({primary_domain}):")
        
        # Add strategic elements
        if strategic_elements:
            insight_parts.append(f"Strategic Elements: {strategic_elements}")
        
        # Add business implications
        if business_implications:
            insight_parts.append(f"Business Implications: {business_implications}")
        
        # Add domain context
        if len(detected_domains) > 1:
            insight_parts.append(f"Cross-domain Impact: {', '.join(detected_domains)}")
        
        # Add key question context (summarized)
        question_summary = self._summarize_question_context(question)
        if question_summary:
            insight_parts.append(f"Context: {question_summary}")
        
        return " | ".join(insight_parts)
    
    def _create_bi_operational_summary(
        self,
        question: str,
        response: str,
        content_info: Dict[str, Any]
    ) -> str:
        """Create a BI operational summary for short-term storage (SUMMARIZED)"""
        
        primary_context = content_info.get("primary_context", "unknown")
        detected_contexts = content_info.get("detected_contexts", [])
        has_quantitative_data = content_info.get("has_quantitative_data", False)
        has_actionable_insights = content_info.get("has_actionable_insights", False)
        
        # Extract key BI findings from the response
        bi_findings = self._extract_bi_key_findings(response)
        quantitative_data = self._extract_quantitative_summary(response) if has_quantitative_data else None
        actionable_items = self._extract_actionable_items(response) if has_actionable_insights else None
        
        # Create a concise BI summary (NOT raw content)
        summary_parts = []
        
        summary_parts.append(f"📊 BI SUMMARY ({primary_context}):")
        
        # Add key findings
        if bi_findings:
            summary_parts.append(f"Findings: {bi_findings}")
        
        # Add quantitative data summary
        if quantitative_data:
            summary_parts.append(f"Data: {quantitative_data}")
        
        # Add actionable insights
        if actionable_items:
            summary_parts.append(f"Actions: {actionable_items}")
        
        # Add context breadth
        if len(detected_contexts) > 1:
            summary_parts.append(f"Contexts: {', '.join(detected_contexts)}")
        
        # Add question context (summarized)
        question_summary = self._summarize_question_context(question)
        if question_summary:
            summary_parts.append(f"Query: {question_summary}")
        
        return " | ".join(summary_parts)
    
    def _extract_strategic_elements(self, response: str) -> str:
        """Extract strategic elements from response"""
        strategic_keywords = [
            "chiến lược", "tầm nhìn", "định hướng", "mục tiêu", "kế hoạch",
            "strategy", "vision", "direction", "goal", "plan"
        ]
        
        sentences = response.split('.')
        strategic_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in strategic_keywords):
                strategic_sentences.append(sentence.strip()[:100])  # Limit length
        
        return "; ".join(strategic_sentences[:2])  # Max 2 strategic elements
    
    def _extract_business_implications(self, response: str) -> str:
        """Extract business implications from response"""
        implication_keywords = [
            "tác động", "ảnh hưởng", "kết quả", "hệ quả", "impact", 
            "effect", "result", "consequence", "implication"
        ]
        
        sentences = response.split('.')
        implication_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in implication_keywords):
                implication_sentences.append(sentence.strip()[:100])  # Limit length
        
        return "; ".join(implication_sentences[:2])  # Max 2 implications
    
    def _extract_bi_key_findings(self, response: str) -> str:
        """Extract key BI findings from response"""
        finding_keywords = [
            "phát hiện", "kết quả", "cho thấy", "indicates", "shows", 
            "reveals", "finding", "result", "analysis"
        ]
        
        sentences = response.split('.')
        finding_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in finding_keywords):
                finding_sentences.append(sentence.strip()[:80])  # Limit length
        
        return "; ".join(finding_sentences[:2])  # Max 2 findings
    
    def _extract_quantitative_summary(self, response: str) -> str:
        """Extract quantitative data summary"""
        import re
        
        # Find numbers with context
        number_matches = re.findall(r'\d+[%\w\s]*(?:triệu|tỷ|nghìn|million|billion|VND|USD)', response, re.IGNORECASE)
        percentage_matches = re.findall(r'\d+%', response)
        
        quantitative_items = []
        quantitative_items.extend(number_matches[:3])  # Max 3 numbers
        quantitative_items.extend(percentage_matches[:2])  # Max 2 percentages
        
        return ", ".join(quantitative_items) if quantitative_items else None
    
    def _extract_actionable_items(self, response: str) -> str:
        """Extract actionable items from response"""
        action_keywords = [
            "nên", "khuyến nghị", "đề xuất", "cần", "should", "recommend", 
            "suggest", "need", "action", "next"
        ]
        
        sentences = response.split('.')
        action_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in action_keywords):
                action_sentences.append(sentence.strip()[:80])  # Limit length
        
        return "; ".join(action_sentences[:2])  # Max 2 actions
    
    def _summarize_question_context(self, question: str) -> str:
        """Summarize question context"""
        # Extract key terms from question
        key_terms = []
        
        # Business terms
        business_terms = ["doanh thu", "lợi nhuận", "bán hàng", "khách hàng", "sản xuất", "tài chính"]
        for term in business_terms:
            if term in question.lower():
                key_terms.append(term)
        
        # Time terms
        time_terms = ["tháng", "năm", "quý", "tuần", "ngày"]
        for term in time_terms:
            if term in question.lower():
                key_terms.append(term)
        
        # Analysis terms
        analysis_terms = ["phân tích", "báo cáo", "thống kê", "so sánh"]
        for term in analysis_terms:
            if term in question.lower():
                key_terms.append(term)
        
        return ", ".join(key_terms[:4]) if key_terms else question[:50]  # Max 4 terms or first 50 chars 