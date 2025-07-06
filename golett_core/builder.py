from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from golett_core.interfaces import (
    ToolInterface,
    SessionManagerInterface,
    MemoryStoreInterface,
    CrewInterface,
    OrchestratorInterface,
    VectorStoreInterface,
    KnowledgeInterface,
    GraphStoreInterface,
)
from golett_core.crew.spec import CrewSpec, default_specs, register_spec, KNOWLEDGE_QA_CREW
from golett_core.memory.factory import create_memory_core
from golett_core.executor.master_agent import MasterAgent
from golett_core.crew.factory import CrewFactory
from golett_core.executor.crew_executor import CrewExecutor
from golett_core.data_access.memory_dao import MemoryDAO
from golett_core.data_access.vector_dao import VectorDAO
from golett_core.storage.temp.in_memory_stores import (
    InMemoryMemoryStore,
    InMemoryVectorStore,
    InMemoryGraphStore,
)
from golett_core.session import SessionManager
from golett_core.tools import ToolManager
from golett_core.storage.persistent.postgres_store import PostgresMemoryStore
from golett_core.storage.persistent.qdrant_store import QdrantVectorStore
from golett_core.storage.persistent.postgres_graph_store import PostgresGraphStore
from golett_core.crew import CrewManager
from golett_core.knowledge import KnowledgeManager
from golett_core.crew.rag_orchestrator import RAGOrchestrator
from golett_core.schemas import Session, ChatMessage, Document
from golett_core.cache import InMemoryCache
from golett_core.session.manager import InMemorySessionManager
from golett_core.data_access.graph_dao import GraphDAO
from golett_core.routing.intent_router import IntentRouter
from golett_core.scheduler import SchedulerService, AdaptiveScheduler
from golett_core.memory.workers.promotion_worker import PromotionWorker
from golett_core.memory.workers.ttl_pruner import TTLPruner
from golett_core.events import EventBus, PeriodicTick, AgentProduced, NewTurn

class GolettApp:
    """
    The final assembled Golett application, ready to handle chat.
    """
    def __init__(
        self,
        orchestrator: OrchestratorInterface,
        session_manager: SessionManagerInterface,
        bus: EventBus,
    ):
        self.orchestrator = orchestrator
        self.session_manager = session_manager
        self.bus = bus

    async def chat(self, session_id, user_input) -> str:
        # The orchestrator is no longer session-aware, so the app layer
        # is responsible for managing history.
        user_message = ChatMessage(session_id=session_id, role="user", content=user_input)
        await self.session_manager.add_message(session_id, user_message)
        
        # Emit NewTurn so workers & retrieval refreshers react
        try:

            await self.bus.publish(
                NewTurn(
                    session_id=session_id,
                    user_id=str(user_message.id),  # using message id as proxy
                    turn_id=str(user_message.id),
                    text=user_input,
                )
            )
        except Exception:
            pass
        
        assistant_response = await self.orchestrator.run(user_input)
        
        try:
            await self.bus.publish(
                AgentProduced(
                    session_id=session_id,
                    agent_id="assistant",
                    turn_id=str(user_message.id),
                    content=assistant_response,
                )
            )
        except Exception:
            pass
        
        # The RAG orchestrator's run() method now saves the assistant reply
        return assistant_response


class GolettBuilder:
    """
    A fluent builder for constructing a Golett application instance.
    
    This builder allows for customizing core components like memory, knowledge,
    and crew specifications. If a component is not provided, a default
    in-memory implementation will be used.
    """

    def __init__(self):
        self.tool_core: ToolInterface = ToolManager()
        self.crew_core: CrewInterface = CrewManager()
        self.knowledge_core: KnowledgeInterface = KnowledgeManager(collection_name="default_knowledge")
        
        # Low-level stores – default to in-memory so users don't need
        # external services for quick experiments. Switch to persistent
        # with `with_persistent_stores()`.
        self._rel_store: MemoryStoreInterface = InMemoryMemoryStore()
        self._vec_store: VectorStoreInterface = InMemoryVectorStore()
        self._graph_store: GraphStoreInterface = InMemoryGraphStore()

        # Unified memory interface assembled later
        self.memory_core: Optional[MemoryStoreInterface] = None
        self.session_manager_core: Optional[SessionManagerInterface] = None
        self.orchestrator_core: Optional[OrchestratorInterface] = None

        # New event bus for reactive core
        self._bus = EventBus()

    def with_memory(self, memory_core: MemoryStoreInterface) -> GolettBuilder:
        """Override the unified memory component (must satisfy MemoryInterface)."""
        self.memory_core = memory_core
        return self

    def with_vectors(self, vector_core: VectorStoreInterface) -> GolettBuilder:
        self._vec_store = vector_core
        return self

    def with_knowledge(self, knowledge_core: KnowledgeInterface) -> GolettBuilder:
        self.knowledge_core = knowledge_core
        return self

    def with_tools(self, tool_core: ToolInterface) -> GolettBuilder:
        self.tool_core = tool_core
        return self

    def with_crews(self, crew_core: CrewInterface) -> GolettBuilder:
        self.crew_core = crew_core
        return self

    def with_session_manager(
        self, session_manager_core: SessionManagerInterface
    ) -> GolettBuilder:
        self.session_manager_core = session_manager_core
        return self

    def with_orchestrator(self, orchestrator: OrchestratorInterface) -> GolettBuilder:
        self.orchestrator_core = orchestrator
        return self
        
    def with_in_memory_stores(self) -> GolettBuilder:
        """Explicitly switch every persistence layer to in-memory mocks."""
        self.session_manager_core = InMemorySessionManager()
        self._rel_store = InMemoryMemoryStore()
        self._vec_store = InMemoryVectorStore()
        self._graph_store = InMemoryGraphStore()
        return self

    def with_persistent_stores(self) -> GolettBuilder:
        """Use Postgres + Qdrant + PG graph for full durability."""
        self._rel_store = PostgresMemoryStore()
        self._vec_store = QdrantVectorStore()
        self._graph_store = PostgresGraphStore()
        return self

    def build(self) -> GolettApp:
        # ------------------------------------------------------------------
        # 1. Build unified memory core (if caller didn't supply one)
        # ------------------------------------------------------------------

        if self.memory_core is None:
            memory_dao = MemoryDAO(self._rel_store)
            vector_dao = VectorDAO(self._vec_store)
            graph_dao = GraphDAO(self._graph_store)
            self.memory_core = create_memory_core(
                memory_dao=memory_dao,
                vector_dao=vector_dao,
                graph_dao=graph_dao,
            )

            # Inject event bus so save_message publishes MemoryWritten
            self.memory_core.bus = self._bus  # type: ignore[attr-defined]

        # ------------------------------------------------------------------
        # 2. Session manager (chat history metadata)
        # ------------------------------------------------------------------

        if self.session_manager_core is None:
            self.session_manager_core = SessionManager(
                session_store=self._rel_store,
                history_store=self._rel_store,
                cache_client=InMemoryCache(),
            )

        if self.orchestrator_core is None:
            self.orchestrator_core = RAGOrchestrator(
                memory_core=self.memory_core,
                knowledge_handler=self.knowledge_core,
                router=IntentRouter(),
            )

        # ------------------------------------------------------------------
        # 3. Fire up NEW event-driven AdaptiveScheduler ----------------------
        # ------------------------------------------------------------------

        try:
            ttl_pruner = TTLPruner(
                self.memory_core.in_session_store,  # type: ignore[attr-defined]
                self.memory_core.short_term_store,  # type: ignore[attr-defined]
                memory_dao,
            )

            promotion_worker = PromotionWorker(
                self.memory_core.short_term_store,  # type: ignore[attr-defined]
                self.memory_core.long_term_store,  # type: ignore[attr-defined]
                memory_dao,
            )

            adaptive = AdaptiveScheduler(
                bus=self._bus,
                workers=[ttl_pruner, promotion_worker],
            )

            import asyncio

            # Periodic ticker – fallback safety every 10 minutes
            async def _ticker(bus: EventBus, interval: int = 600):
                while True:
                    await asyncio.sleep(interval)
                    await bus.publish(PeriodicTick(name="fallback"))

            asyncio.create_task(adaptive.start())
            asyncio.create_task(_ticker(self._bus))

        except Exception as exc:  # pragma: no cover
            print(f"[GolettBuilder] AdaptiveScheduler bootstrap failed: {exc}")

        # ------------------------------------------------------------------
        return GolettApp(
            orchestrator=self.orchestrator_core,
            session_manager=self.session_manager_core,
            bus=self._bus,
        ) 