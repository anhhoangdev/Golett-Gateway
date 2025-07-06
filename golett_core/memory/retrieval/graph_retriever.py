from __future__ import annotations

"""GraphMemoryRetriever – utility that bridges natural-language mentions to the
knowledge-graph via ``GraphDAO``.

Typical usage::

    retriever = GraphMemoryRetriever(graph_dao)
    nodes = await retriever.fetch_related_nodes("Who owns Component X?", depth=2)

Returned ``Node`` objects can then be passed to :class:`ReRanker` so that
memory snippets linked in the graph receive a relational score boost.
"""

from uuid import UUID, uuid5, NAMESPACE_OID
from typing import List

# Contracts / types
from golett_core.data_access.graph_dao import GraphDAO
from golett_core.memory.retrieval.entity_extraction import extract_entities
from golett_core.schemas.memory import Node
from golett_core.interfaces import GraphRetrieverInterface

__all__ = ["GraphMemoryRetriever"]


# pylint: disable=too-few-public-methods
class GraphMemoryRetriever(GraphRetrieverInterface):
    """Lightweight adapter that resolves entity strings to graph nodes/edges."""

    def __init__(self, graph_dao: GraphDAO):
        self._dao = graph_dao

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _entities_to_uuids(entities: List[str]) -> List[UUID]:
        """Stable mapping Entity-ID ←→ UUID via UUIDv5.

        The same algorithm is used by :class:`GraphWorker` when persisting
        nodes, guaranteeing that we hit the exact same identifiers here.
        """
        return [uuid5(NAMESPACE_OID, ent) for ent in entities]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch_related_nodes(self, query: str, depth: int = 1) -> List[Node]:
        """Return nodes within *depth* hops of entities mentioned in *query*."""
        entities = extract_entities(query)
        if not entities:
            return []

        node_ids = self._entities_to_uuids(entities)
        try:
            # Delegate the heavy lifting to the store implementation (SQL/Neo4j…)
            nodes = await self._dao.get_graph_neighborhood(node_ids, depth)
            return nodes
        except Exception:  # pragma: no cover – surface area depends on store
            # In early builds we don't want graph errors to break user queries.
            return [] 