from typing import Any, Dict, List, Optional

from crewai.knowledge import Knowledge
from golett.memory.memory_manager import MemoryManager
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class GolettKnowledgeAdapter:
    """
    Adapter that bridges CrewAI's Knowledge system with Golett's MemoryManager.
    
    This class allows using CrewAI's knowledge sources with Golett's memory
    system, enabling knowledge retrieval for crews while maintaining conversation context.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the adapter.
        
        Args:
            memory_manager: The Golett memory manager instance
        """
        self.memory_manager = memory_manager
        self.knowledge_stores = {}
        
        logger.info("Initialized Golett Knowledge Adapter")
    
    def create_crew_knowledge(
        self, 
        collection_name: str, 
        sources: List[Any],
        embedder: Optional[Dict[str, Any]] = None
    ) -> Knowledge:
        """
        Create a CrewAI knowledge object with the provided sources.
        
        Args:
            collection_name: Name for the knowledge collection
            sources: List of CrewAI knowledge sources
            embedder: Optional embedder configuration
            
        Returns:
            The initialized Knowledge object
        """
        # Create CrewAI knowledge object with sources
        knowledge = Knowledge(
            collection_name=collection_name,
            sources=sources,
            embedder=embedder
        )
        
        # Initialize sources
        knowledge.add_sources()
        
        # Store for later use
        self.knowledge_stores[collection_name] = knowledge
        
        logger.info(f"Created CrewAI knowledge collection: {collection_name}")
        return knowledge
    
    def retrieve_for_query(
        self, 
        query: str, 
        session_id: str, 
        collection_name: Optional[str] = None,
        crew_limit: int = 3,
        memory_limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information from both CrewAI knowledge and Golett memory.
        
        Args:
            query: The query to search for
            session_id: The session ID for memory retrieval
            collection_name: Optional specific knowledge collection to query
            crew_limit: Maximum number of results from CrewAI knowledge
            memory_limit: Maximum number of results from memory
            
        Returns:
            Combined list of relevant information
        """
        results = []
        
        # Get results from CrewAI knowledge if available
        if collection_name and collection_name in self.knowledge_stores:
            knowledge = self.knowledge_stores[collection_name]
            crew_results = knowledge.query(
                query=[query], 
                results_limit=crew_limit
            )
            results.extend(crew_results)
        elif not collection_name:
            # Query all knowledge stores if no specific one is provided
            for name, knowledge in self.knowledge_stores.items():
                crew_results = knowledge.query(
                    query=[query], 
                    results_limit=crew_limit
                )
                results.extend(crew_results)
        
        # Get results from memory
        memory_results = self.memory_manager.retrieve_context(
            session_id=session_id,
            query=query,
            limit=memory_limit
        )
        
        results.extend(memory_results)
        
        logger.debug(f"Retrieved {len(results)} items for query")
        return results 