"""
Enhanced Context Management for Golett

This module provides advanced context retrieval patterns that combine
semantic search, cross-session insights, and intelligent context aggregation.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.contextual.context_manager import ContextManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)


class ContextRetrievalStrategy(Enum):
    """Strategies for context retrieval"""
    COMPREHENSIVE = "comprehensive"  # Full context with semantic search
    CONTEXTUAL = "contextual"       # Recent context with some semantic lookup
    CONVERSATIONAL = "conversational"  # Light context for casual conversation
    FOCUSED = "focused"             # Targeted context for specific domains


class EnhancedContextManager(ContextManager):
    """
    Enhanced context manager with advanced retrieval patterns.
    
    This extends the base ContextManager with sophisticated context
    retrieval strategies used in domain-specific chatbots.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize the enhanced context manager"""
        super().__init__(memory_manager)
        self.memory_manager = memory_manager
        
        # Cache for frequently accessed contexts
        self._context_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        logger.info("Enhanced context manager initialized")
    
    def get_enhanced_context(
        self,
        session_id: str,
        question: str,
        strategy: ContextRetrievalStrategy = ContextRetrievalStrategy.COMPREHENSIVE,
        domain: str = None,
        conversation_type: str = None,
        include_cross_session: bool = True,
        max_context_age_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get enhanced context using specified retrieval strategy.
        
        Args:
            session_id: Session identifier
            question: The question/query for context
            strategy: Context retrieval strategy
            domain: Domain for domain-specific context
            conversation_type: Type of conversation for context optimization
            include_cross_session: Whether to include cross-session context
            max_context_age_days: Maximum age of context to retrieve
            
        Returns:
            Enhanced context dictionary with multiple context types
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(session_id, question, strategy, domain)
            cached_context = self._get_cached_context(cache_key)
            if cached_context:
                logger.debug(f"Retrieved context from cache for session {session_id}")
                return cached_context
            
            # Get context based on strategy
            if strategy == ContextRetrievalStrategy.COMPREHENSIVE:
                context = self._get_comprehensive_context(
                    session_id, question, domain, include_cross_session, max_context_age_days
                )
            elif strategy == ContextRetrievalStrategy.CONTEXTUAL:
                context = self._get_contextual_context(
                    session_id, question, domain, include_cross_session
                )
            elif strategy == ContextRetrievalStrategy.CONVERSATIONAL:
                context = self._get_conversational_context(session_id, question)
            elif strategy == ContextRetrievalStrategy.FOCUSED:
                context = self._get_focused_context(
                    session_id, question, domain, conversation_type
                )
            else:
                context = self._get_basic_context(session_id, question)
            
            # Add metadata
            context["retrieval_metadata"] = {
                "strategy": strategy.value,
                "domain": domain,
                "conversation_type": conversation_type,
                "retrieved_at": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            # Cache the result
            self._cache_context(cache_key, context)
            
            logger.info(f"Retrieved {strategy.value} context for session {session_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return self._get_fallback_context(session_id, question)
    
    def _get_comprehensive_context(
        self,
        session_id: str,
        question: str,
        domain: str,
        include_cross_session: bool,
        max_context_age_days: int
    ) -> Dict[str, Any]:
        """Get comprehensive context with full semantic search and cross-session insights"""
        
        # 1. Get recent conversation context
        recent_conversation = self.memory_manager.get_session_history(
            session_id=session_id,
            limit=5,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
        )
        
        # 2. Semantic search across all layers
        semantic_memories = self._semantic_memory_search(
            session_id=session_id,
            query=question,
            limit=5,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
        )
        
        # 3. Cross-session insights if enabled
        cross_session_insights = []
        if include_cross_session:
            cross_session_insights = self._get_cross_session_insights(
                session_id=session_id,
                query=question,
                domain=domain,
                limit=3,
                max_age_days=max_context_age_days
            )
        
        # 4. Related conversation summaries
        related_summaries = self._get_related_conversation_summaries(
            session_id=session_id,
            query=question,
            limit=3,
            include_cross_session=include_cross_session
        )
        
        # 5. Domain-specific context if domain provided
        domain_context = []
        if domain:
            domain_context = self._get_domain_specific_context(
                session_id=session_id,
                query=question,
                domain=domain,
                limit=3
            )
        
        return {
            "recent_conversation": recent_conversation,
            "semantic_memories": semantic_memories,
            "cross_session_insights": cross_session_insights,
            "related_summaries": related_summaries,
            "domain_context": domain_context,
            "context_type": "comprehensive"
        }
    
    def _get_contextual_context(
        self,
        session_id: str,
        question: str,
        domain: str,
        include_cross_session: bool
    ) -> Dict[str, Any]:
        """Get contextual context with recent focus and some semantic lookup"""
        
        # 1. Get recent conversation with more detail
        recent_conversation = self.memory_manager.get_session_history(
            session_id=session_id,
            limit=8,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
        )
        
        # 2. Limited semantic search focusing on recent memories
        semantic_memories = self._semantic_memory_search(
            session_id=session_id,
            query=question,
            limit=3,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
        )
        
        # 3. Limited cross-session if enabled
        cross_session_insights = []
        if include_cross_session:
            cross_session_insights = self._get_cross_session_insights(
                session_id=session_id,
                query=question,
                domain=domain,
                limit=2,
                max_age_days=7  # More recent for contextual
            )
        
        return {
            "recent_conversation": recent_conversation,
            "semantic_memories": semantic_memories,
            "cross_session_insights": cross_session_insights,
            "context_type": "contextual"
        }
    
    def _get_conversational_context(self, session_id: str, question: str) -> Dict[str, Any]:
        """Get light context for conversational interactions"""
        
        # 1. Recent conversation only
        recent_conversation = self.memory_manager.get_session_history(
            session_id=session_id,
            limit=5,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
        )
        
        # 2. User preferences and light semantic search
        user_preferences = self._get_user_preferences(session_id)
        
        # 3. Light semantic search for user patterns
        user_patterns = self._semantic_memory_search(
            session_id=session_id,
            query=f"user preferences greeting conversation {question}",
            limit=2,
            include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
        )
        
        return {
            "recent_conversation": recent_conversation,
            "user_preferences": user_preferences,
            "user_patterns": user_patterns,
            "context_type": "conversational"
        }
    
    def _get_focused_context(
        self,
        session_id: str,
        question: str,
        domain: str,
        conversation_type: str
    ) -> Dict[str, Any]:
        """Get focused context for specific domain and conversation type"""
        
        # 1. Targeted conversation history based on type
        history_limit = self._get_history_limit_for_type(conversation_type)
        recent_conversation = self.memory_manager.get_session_history(
            session_id=session_id,
            limit=history_limit,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
        )
        
        # 2. Domain-specific semantic search
        domain_memories = self._semantic_memory_search(
            session_id=session_id,
            query=f"{domain} {question}",
            limit=4,
            include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
            filter_by_domain=domain
        )
        
        # 3. Type-specific context
        type_specific_context = self._get_type_specific_context(
            session_id=session_id,
            conversation_type=conversation_type,
            domain=domain,
            limit=3
        )
        
        return {
            "recent_conversation": recent_conversation,
            "domain_memories": domain_memories,
            "type_specific_context": type_specific_context,
            "context_type": "focused"
        }
    
    def _semantic_memory_search(
        self,
        session_id: str,
        query: str,
        limit: int = 5,
        include_layers: List[MemoryLayer] = None,
        filter_by_domain: str = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search with enhanced filtering and formatting"""
        try:
            if include_layers is None:
                include_layers = [MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
            
            # Use the memory manager's search capabilities
            results = self.memory_manager.search_across_all_layers(
                query=query,
                session_id=session_id,
                limit=limit,
                include_layer_weights=True
            )
            
            # Filter by domain if specified
            if filter_by_domain:
                results = [
                    result for result in results
                    if result.get("metadata", {}).get("domain") == filter_by_domain
                ]
            
            # Format results with enhanced metadata
            formatted_results = []
            for result in results:
                formatted_result = {
                    "content": result.get("data", ""),
                    "metadata": result.get("metadata", {}),
                    "similarity_score": result.get("score", 0.0),
                    "weighted_score": result.get("weighted_score", result.get("score", 0.0)),
                    "memory_layer": result.get("metadata", {}).get("searched_in_layer", "unknown"),
                    "timestamp": result.get("metadata", {}).get("timestamp", ""),
                    "context_type": result.get("metadata", {}).get("type", "general"),
                    "domain": result.get("metadata", {}).get("domain", "unknown")
                }
                formatted_results.append(formatted_result)
            
            logger.debug(f"Found {len(formatted_results)} semantic memories for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.warning(f"Error in semantic memory search: {e}")
            return []
    
    def _get_cross_session_insights(
        self,
        session_id: str,
        query: str,
        domain: str,
        limit: int = 3,
        max_age_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get insights from other sessions that might be relevant"""
        try:
            # Use ContextManager's cross-session capabilities
            cross_session_results = self.retrieve_bi_context(
                session_id=session_id,
                query=query,
                limit=limit,
                include_layers=[MemoryLayer.LONG_TERM],
                cross_session=True
            )
            
            # Filter by age and domain
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            filtered_insights = []
            
            for insight in cross_session_results:
                # Check age
                timestamp_str = insight.get("metadata", {}).get("timestamp", "")
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if timestamp < cutoff_date:
                            continue
                    except:
                        pass
                
                # Check domain if specified
                if domain and insight.get("metadata", {}).get("domain") != domain:
                    continue
                
                formatted_insight = {
                    "insight": insight.get("data", ""),
                    "source_session": insight.get("metadata", {}).get("session_id", "unknown"),
                    "importance": insight.get("importance", 0.0),
                    "timestamp": insight.get("metadata", {}).get("timestamp", ""),
                    "domain": insight.get("metadata", {}).get("domain", "unknown"),
                    "context_type": insight.get("metadata", {}).get("type", "unknown")
                }
                filtered_insights.append(formatted_insight)
            
            logger.debug(f"Found {len(filtered_insights)} cross-session insights")
            return filtered_insights
            
        except Exception as e:
            logger.warning(f"Error getting cross-session insights: {e}")
            return []
    
    def _get_related_conversation_summaries(
        self,
        session_id: str,
        query: str,
        limit: int = 3,
        include_cross_session: bool = False
    ) -> List[Dict[str, Any]]:
        """Get related conversation summaries"""
        try:
            # Use ContextManager's conversation summary capabilities
            summary_results = self.retrieve_conversation_summaries(
                session_id=session_id,
                query=query,
                limit=limit,
                include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
                cross_session=include_cross_session
            )
            
            formatted_summaries = []
            for summary in summary_results:
                formatted_summary = {
                    "summary": summary.get("data", ""),
                    "topics": summary.get("metadata", {}).get("topics", []),
                    "timestamp": summary.get("metadata", {}).get("start_time", ""),
                    "conversation_type": summary.get("metadata", {}).get("conversation_type", "unknown"),
                    "session_id": summary.get("metadata", {}).get("session_id", "unknown"),
                    "domain": summary.get("metadata", {}).get("domain", "unknown")
                }
                formatted_summaries.append(formatted_summary)
            
            logger.debug(f"Found {len(formatted_summaries)} related conversation summaries")
            return formatted_summaries
            
        except Exception as e:
            logger.warning(f"Error getting related conversation summaries: {e}")
            return []
    
    def _get_domain_specific_context(
        self,
        session_id: str,
        query: str,
        domain: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get domain-specific context"""
        try:
            # Search for domain-specific context
            domain_results = self.memory_manager.retrieve_context(
                session_id=session_id,
                query=f"{domain} {query}",
                context_types=[f"{domain}_data", f"{domain}_insight", f"{domain}_knowledge"],
                limit=limit,
                include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
                cross_session=True
            )
            
            formatted_context = []
            for result in domain_results:
                formatted_result = {
                    "content": result.get("data", ""),
                    "context_type": result.get("metadata", {}).get("type", "unknown"),
                    "domain": result.get("metadata", {}).get("domain", domain),
                    "importance": result.get("importance", 0.0),
                    "timestamp": result.get("metadata", {}).get("timestamp", "")
                }
                formatted_context.append(formatted_result)
            
            logger.debug(f"Found {len(formatted_context)} domain-specific context items")
            return formatted_context
            
        except Exception as e:
            logger.warning(f"Error getting domain-specific context: {e}")
            return []
    
    def _get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences from session metadata"""
        try:
            # This would typically be implemented by the SessionManager
            # For now, return empty dict as placeholder
            return {}
        except Exception as e:
            logger.warning(f"Error getting user preferences: {e}")
            return {}
    
    def _get_type_specific_context(
        self,
        session_id: str,
        conversation_type: str,
        domain: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get context specific to conversation type"""
        try:
            # Search for type-specific patterns
            type_query = f"{conversation_type} {domain}"
            type_results = self.memory_manager.retrieve_context(
                session_id=session_id,
                query=type_query,
                context_types=["conversation_pattern", "interaction_history"],
                limit=limit,
                include_layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
            )
            
            formatted_results = []
            for result in type_results:
                formatted_result = {
                    "content": result.get("data", ""),
                    "conversation_type": result.get("metadata", {}).get("conversation_type", conversation_type),
                    "pattern_type": result.get("metadata", {}).get("pattern_type", "unknown"),
                    "frequency": result.get("metadata", {}).get("frequency", 1),
                    "timestamp": result.get("metadata", {}).get("timestamp", "")
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.warning(f"Error getting type-specific context: {e}")
            return []
    
    def _get_history_limit_for_type(self, conversation_type: str) -> int:
        """Get appropriate history limit based on conversation type"""
        limits = {
            "data_analysis": 5,
            "follow_up": 8,
            "clarification": 6,
            "explanation": 6,
            "conversational": 3,
            "greeting": 2,
            "help": 4
        }
        return limits.get(conversation_type, 5)
    
    def _get_basic_context(self, session_id: str, question: str) -> Dict[str, Any]:
        """Get basic context as fallback"""
        try:
            recent_conversation = self.memory_manager.get_session_history(
                session_id=session_id,
                limit=3,
                include_layers=[MemoryLayer.IN_SESSION]
            )
            
            return {
                "recent_conversation": recent_conversation,
                "context_type": "basic"
            }
        except Exception as e:
            logger.error(f"Error getting basic context: {e}")
            return {"context_type": "error", "error": str(e)}
    
    def _get_fallback_context(self, session_id: str, question: str) -> Dict[str, Any]:
        """Get fallback context when all else fails"""
        return {
            "recent_conversation": [],
            "semantic_memories": [],
            "cross_session_insights": [],
            "context_type": "fallback",
            "error": "Context retrieval failed, using fallback"
        }
    
    # Caching methods
    
    def _get_cache_key(self, session_id: str, question: str, strategy: ContextRetrievalStrategy, domain: str) -> str:
        """Generate cache key for context"""
        import hashlib
        key_string = f"{session_id}:{question[:100]}:{strategy.value}:{domain or 'none'}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_context(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get context from cache if valid"""
        if cache_key in self._context_cache:
            cached_item = self._context_cache[cache_key]
            if datetime.now().timestamp() - cached_item["timestamp"] < self._cache_ttl:
                return cached_item["context"]
            else:
                # Remove expired cache
                del self._context_cache[cache_key]
        return None
    
    def _cache_context(self, cache_key: str, context: Dict[str, Any]):
        """Cache context for future use"""
        self._context_cache[cache_key] = {
            "context": context,
            "timestamp": datetime.now().timestamp()
        }
        
        # Clean old cache entries periodically
        if len(self._context_cache) > 100:
            self._clean_cache()
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, value in self._context_cache.items()
            if current_time - value["timestamp"] > self._cache_ttl
        ]
        for key in expired_keys:
            del self._context_cache[key]
        
        logger.debug(f"Cleaned {len(expired_keys)} expired cache entries") 