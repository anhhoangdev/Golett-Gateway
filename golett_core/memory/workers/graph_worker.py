from __future__ import annotations

"""Background worker that converts tagger metadata into graph upserts.

The **GraphWorker** is intentionally stateless – it takes a fully-tagged
``MemoryItem`` (containing the ``entities`` / ``relations`` metadata that
`AutoTagger` now provides) and translates that into node / edge objects for
storage via ``GraphDAO``.

This keeps any DB-specific logic confined to the data-access layer
(`GraphDAO` + ``GraphStoreInterface`` implementations) while higher-level
code simply awaits ``graph_worker.process_item(item)``.
"""

from uuid import uuid5, UUID, NAMESPACE_OID
from typing import List, Dict, Any

from golett_core.data_access.graph_dao import GraphDAO  # Local import to avoid cycles
from golett_core.schemas.memory import MemoryItem, Node

__all__ = ["GraphWorker"]


class GraphWorker:
    """Asynchronous helper that persists entity / relation data to the graph store."""

    def __init__(self, graph_dao: GraphDAO):
        self.dao = graph_dao

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def process_item(self, item: MemoryItem) -> None:  # noqa: D401
        """Upsert nodes & edges based on ``item.metadata``.

        Expected metadata structure (see AutoTagger):

        ```json
        {
          "entities": [{"id": "person:JaneDoe", "type": "Person"}, ...],
          "relations": [
              {"src": "person:JaneDoe", "dst": "acme:ComponentX", "type": "owns"}
          ]
        }
        ```
        """
        if not item.metadata:
            return

        entities = item.metadata.get("entities", [])
        relations = item.metadata.get("relations", [])

        # Nothing to do → early-exit
        if not entities and not relations:
            return

        # ---------------- Nodes ----------------
        id_map: Dict[str, UUID] = {}
        nodes: List[Node] = []

        for ent in entities:
            # Incoming *ent* might be either str or dict
            if isinstance(ent, str):
                ent_id_str, ent_type = ent, "Entity"
            else:
                ent_id_str = ent.get("id")
                ent_type = ent.get("type", "Entity")
            if not ent_id_str:
                continue
            node_uuid = uuid5(NAMESPACE_OID, ent_id_str)
            id_map[ent_id_str] = node_uuid
            nodes.append(Node(id=node_uuid, label=ent_type, properties={"name": ent_id_str}))

        # ---------------- Edges ----------------
        edge_dicts: List[Dict[str, Any]] = []
        for rel in relations:
            src_key = rel.get("src")
            dst_key = rel.get("dst")
            rel_type = rel.get("type", "related_to")
            if not src_key or not dst_key:
                continue
            # Ensure nodes exist in id_map (they might not be part of *entities*)
            for key in (src_key, dst_key):
                if key not in id_map:
                    id_map[key] = uuid5(NAMESPACE_OID, key)
                    nodes.append(Node(id=id_map[key], label="Entity", properties={"name": key}))
            edge_dicts.append(
                {
                    "src": id_map[src_key],
                    "dst": id_map[dst_key],
                    "type": rel_type,
                    "metadata": {"source_item": str(item.id)},
                }
            )

        # ---------------- Persist ----------------
        if nodes:
            await self.dao.upsert_nodes(nodes)
        if edge_dicts:
            await self.dao.upsert_edges(edge_dicts) 