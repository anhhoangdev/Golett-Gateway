from __future__ import annotations

"""Data Access Object for graph storage operations.

This mirrors the adapter that previously lived in **golett_api** but is now
part of the *core* layer so that other core components (e.g. ``GraphWorker``)
can depend on it without creating an unwanted layering violation.
"""

from typing import List, Dict, Any
from uuid import UUID

from golett_core.interfaces import GraphStoreInterface
from golett_core.schemas.memory import Node

__all__ = ["GraphDAO"]


class GraphDAO:
    """Thin abstraction around a :pyclass:`GraphStoreInterface`."""

    def __init__(self, store: GraphStoreInterface):
        self.store = store

    # ------------------------------------------------------------------
    # Node helpers
    # ------------------------------------------------------------------

    async def upsert_nodes(self, nodes: List[Node]):  # noqa: D401
        """Create or merge the provided *nodes* in the underlying graph store."""
        await self.store.upsert_nodes(nodes)

    async def get_nodes(self, node_ids: List[UUID]) -> List[Node]:  # noqa: D401
        # Not part of the protocol yet but some stores might support it.
        if hasattr(self.store, "get_nodes"):
            return await self.store.get_nodes(node_ids)  # type: ignore[attr-defined]
        # Fallback – fetch neighbourhood of depth 0 which should return the nodes themselves
        return await self.store.neighborhood(node_ids, depth=0)

    # ------------------------------------------------------------------
    # Edge helpers
    # ------------------------------------------------------------------

    async def upsert_edges(self, edges: List[Dict[str, Any]]):  # noqa: D401
        """Create or merge *edges*.

        Edge dict structure is left to the concrete store implementation but
        should at minimum contain ``src`` (UUID), ``dst`` (UUID), and ``type``.
        """
        await self.store.upsert_edges(edges)

    async def get_graph_neighborhood(
        self, entity_ids: List[UUID], depth: int = 1
    ) -> List[Node]:  # noqa: D401
        """Return nodes within *depth* hops from the *entity_ids* set."""
        return await self.store.neighborhood(entity_ids, depth)

    # Alias maintained for compatibility
    async def neighborhood(self, node_ids: List[UUID], depth: int):  # noqa: D401
        return await self.get_graph_neighborhood(node_ids, depth) 