from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from golett_core.schemas import Session, ChatMessage, Document
from golett_core.interfaces import (
    MemoryStoreInterface,
    VectorStoreInterface,
    MemoryStorageInterface,
    GraphStoreInterface,
)
from golett_core.schemas.memory import MemoryItem, MemoryType, VectorMatch, Node


class InMemoryMemoryStore(MemoryStoreInterface):
    """Very lightweight, non-persistent store suitable for tests and demos."""

    def __init__(self) -> None:
        self._messages: Dict[UUID, List[ChatMessage]] = {}
        self._memory: Dict[UUID, MemoryItem] = {}

    async def get_messages(self, session_id: UUID, limit: int) -> List[ChatMessage]:
        return list(self._messages.get(session_id, []))[-limit:]

    async def create_memory_item(self, item: MemoryItem) -> UUID:  # type: ignore[override]
        self._memory[item.id] = item
        # Also store messages in _messages for recency fetch if applicable
        if item.type == MemoryType.MESSAGE and item.session_id:
            self._messages.setdefault(item.session_id, []).append(
                ChatMessage(
                    id=item.id,
                    session_id=item.session_id,
                    role="user",  # unknown here
                    content=item.content,
                    created_at=item.created_at,
                )
            )
        return item.id

    async def get_graph_neighborhood(self, node_ids: List[UUID], depth: int):  # type: ignore[override]
        return []


class InMemoryVectorStore(VectorStoreInterface):
    """Extremely naive vector store — returns empty results."""

    async def upsert_vector(
        self,
        collection: str,
        point_id: UUID,
        vector: List[float],
        payload: Dict[str, Any],
    ) -> None:  # noqa: D401
        # No-op for demo
        return None

    async def search(
        self, collection: str, query_vector: List[float], top_k: int
    ) -> List[VectorMatch]:  # noqa: D401
        return []


class InMemoryGraphStore(GraphStoreInterface):
    """Very naive graph implementation kept entirely in-memory.

    **NOTE**: This is *not* intended for production use – it exists so that the
    enhanced memory pipeline (GraphWorker, AutoTagger entity extraction, etc.)
    works out-of-the-box during development / unit-tests without requiring an
    external Neo4j or Postgres instance.
    """

    def __init__(self) -> None:
        # ``_nodes`` keyed by UUID; ``_edges`` is list of dicts with src / dst uuids
        self._nodes: Dict[UUID, Node] = {}
        self._edges: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # GraphStoreInterface
    # ------------------------------------------------------------------

    async def upsert_nodes(self, nodes: List[Node]):  # type: ignore[override]
        for node in nodes:
            # Simple merge – last writer wins for properties
            existing = self._nodes.get(node.id)
            if existing:
                existing.properties.update(node.properties)
            else:
                self._nodes[node.id] = node

    async def upsert_edges(self, edges: List[Dict[str, Any]]):  # type: ignore[override]
        # Deduplicate by (src, dst, type)
        seen = {
            (e["src"], e["dst"], e.get("type")) for e in self._edges
        }
        for edge in edges:
            key = (edge["src"], edge["dst"], edge.get("type"))
            if key not in seen:
                self._edges.append(edge)
                seen.add(key)

    async def neighborhood(self, node_ids: List[UUID], depth: int) -> List[Node]:  # type: ignore[override]
        # Breadth-first search up to *depth* hops
        visited: set[UUID] = set()
        frontier = list(node_ids)
        for _ in range(depth):
            next_frontier: List[UUID] = []
            for nid in frontier:
                if nid in visited:
                    continue
                visited.add(nid)
                # Neighbours are any nodes connected via edges
                neighbours = [
                    e["dst"] for e in self._edges if e["src"] == nid
                ] + [
                    e["src"] for e in self._edges if e["dst"] == nid
                ]
                next_frontier.extend(neighbours)
            frontier = next_frontier
        return [self._nodes[nid] for nid in visited if nid in self._nodes] 