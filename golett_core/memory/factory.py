"""
Factory functions for setting up the unified memory system.

Provides convenient ways to construct GolettMemoryCore with all dependencies.
"""
from __future__ import annotations

from typing import Optional

from golett_core.memory.core import GolettMemoryCore, MemoryProcessor
from golett_core.interfaces import TaggerInterface
from golett_core.memory.processing.tagger import AutoTagger
from golett_core.memory.workers.summarizer_worker import SummarizerWorker
from golett_core.memory.workers.graph_worker import GraphWorker
from golett_core.data_access.memory_dao import MemoryDAO
from golett_core.data_access.vector_dao import VectorDAO
from golett_core.memory.rings.in_session import InSessionStore
from golett_core.memory.rings.short_term import ShortTermStore
from golett_core.memory.rings.long_term import LongTermStore
from golett_core.memory.rings.multi_ring import MultiRingStorage
from golett_core.storage.temp.in_memory_stores import InMemoryGraphStore
from golett_core.data_access.graph_dao import GraphDAO
from golett_core.memory.retrieval.graph_retriever import GraphMemoryRetriever
from golett_core.memory.retrieval.context_forge import ContextForge

def create_memory_core(
    memory_dao: MemoryDAO,
    vector_dao: VectorDAO,
    graph_dao: GraphDAO,
    tagger: Optional[TaggerInterface] = None,
    summarizer_model: str = "gpt-3.5-turbo-0125",
) -> GolettMemoryCore:
    """
    Create a fully configured GolettMemoryCore instance.
    
    Args:
        memory_dao: Configured MemoryDAO for relational storage
        vector_dao: Configured VectorDAO for vector storage  
        tagger: Optional custom tagger (defaults to AutoTagger)
        summarizer_model: OpenAI model for summarization
        graph_dao: Optional custom graph DAO (defaults to in-memory implementation)
    
    Returns:
        Ready-to-use GolettMemoryCore instance
    
    Example:
        ```python
        # Set up your DAOs
        memory_dao = MemoryDAO(postgres_store)
        vector_dao = VectorDAO(qdrant_store)
        
        # Create unified memory system
        memory_core = create_memory_core(memory_dao, vector_dao)
        
        # Use it
        await memory_core.save_message(chat_message)
        context = await memory_core.search(session_id, "What did we discuss about X?")
        ```
    """
    # Build ring stores
    in_session  = InSessionStore(memory_dao)
    short_term  = ShortTermStore(memory_dao, vector_dao)
    long_term   = LongTermStore(memory_dao, vector_dao)

    storage = MultiRingStorage(in_session, short_term, long_term)
    
    # Create processor with content-aware tagging
    processor = MemoryProcessor(tagger or AutoTagger())
    
    # Create summarizer worker
    summarizer = SummarizerWorker(storage, model=summarizer_model)
    
    graph_worker = GraphWorker(graph_dao)
    
    # Graph neighbourhood retriever for relational queries
    graph_retriever = GraphMemoryRetriever(graph_dao)

    # Advanced context builder that can leverage semantic, recency & graph signals
    context_forge = ContextForge(storage, graph_retriever=graph_retriever)
    
    # Assemble the core
    core = GolettMemoryCore(
        storage=storage,
        processor=processor, 
        summarizer=summarizer,
        graph_worker=graph_worker,
        context_forge=context_forge,
    )

    # Expose ring stores for scheduler integration
    core.in_session_store = in_session  # type: ignore[attr-defined]
    core.short_term_store = short_term  # type: ignore[attr-defined]
    core.long_term_store = long_term  # type: ignore[attr-defined]

    return core 