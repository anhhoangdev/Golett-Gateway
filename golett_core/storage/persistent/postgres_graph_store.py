from __future__ import annotations

"""PostgreSQL implementation of ``GraphStoreInterface``.

This keeps things *very* simple: two tables – ``graph_nodes`` and ``graph_edges``.
It is **not** a high-performance property graph engine but it allows the rest of
Golett to persist and query relational knowledge without bringing in Neo4j.

Schema (SQL)::

    CREATE TABLE graph_nodes (
        id          UUID PRIMARY KEY,
        label       TEXT,
        properties  JSONB
    );

    CREATE TABLE graph_edges (
        src         UUID REFERENCES graph_nodes(id),
        dst         UUID REFERENCES graph_nodes(id),
        type        TEXT,
        metadata    JSONB,
        PRIMARY KEY (src, dst, type)
    );

If you use a migration tool (Alembic/Flyway) create equivalent DDL.  This class
uses *sync* SQLAlchemy for brevity – all ``GraphStoreInterface`` methods remain
``async`` so they can be awaited uniformly elsewhere.
"""

import os
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import (
    create_engine,
    Table,
    Column,
    MetaData,
    String,
    JSON,
    ForeignKey,
    select,
    insert,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.exc import IntegrityError

from golett_core.interfaces import GraphStoreInterface
from golett_core.schemas.memory import Node

__all__ = ["PostgresGraphStore"]


class PostgresGraphStore(GraphStoreInterface):
    """Naïve PG implementation suitable for small/medium graphs."""

    def __init__(self, dsn: str | None = None):
        self._dsn = dsn or os.getenv("POSTGRES_DSN")
        if not self._dsn:
            raise RuntimeError("POSTGRES_DSN env var not set and DSN not provided")

        self._engine = create_engine(self._dsn)
        self._meta = MetaData()

        # Reflect or define tables
        self._nodes = Table(
            "graph_nodes",
            self._meta,
            Column("id", PG_UUID(as_uuid=True), primary_key=True),
            Column("label", String(255)),
            Column("properties", JSON),
            extend_existing=True,
        )
        self._edges = Table(
            "graph_edges",
            self._meta,
            Column("src", PG_UUID(as_uuid=True), ForeignKey("graph_nodes.id")),
            Column("dst", PG_UUID(as_uuid=True), ForeignKey("graph_nodes.id")),
            Column("type", String(255)),
            Column("metadata", JSON),
            # Composite PK prevents duplicates
            extend_existing=True,
        )
        self._meta.create_all(self._engine)

    # ------------------------------------------------------------------
    # GraphStoreInterface
    # ------------------------------------------------------------------

    async def upsert_nodes(self, nodes: List[Node]):  # noqa: D401
        if not nodes:
            return
        values = [
            {
                "id": n.id,
                "label": n.label,
                "properties": n.properties,
            }
            for n in nodes
        ]
        with self._engine.begin() as conn:
            for val in values:
                try:
                    conn.execute(insert(self._nodes).values(**val))
                except IntegrityError:
                    # Already exists – perform shallow update of label/properties
                    stmt = (
                        self._nodes.update()
                        .where(self._nodes.c.id == val["id"])
                        .values(label=val["label"], properties=val["properties"])
                    )
                    conn.execute(stmt)

    async def upsert_edges(self, edges: List[Dict[str, Any]]):  # noqa: D401
        if not edges:
            return
        with self._engine.begin() as conn:
            for edge in edges:
                try:
                    conn.execute(insert(self._edges).values(**edge))
                except IntegrityError:
                    # Edge already present – ignore duplicates
                    pass

    async def neighborhood(self, node_ids: List[UUID], depth: int) -> List[Node]:  # noqa: D401
        if not node_ids or depth <= 0:
            return []
        collected: Dict[UUID, Node] = {}
        frontier = list(node_ids)
        with self._engine.connect() as conn:
            for _ in range(depth):
                if not frontier:
                    break
                q = select(
                    self._edges.c.src,
                    self._edges.c.dst,
                ).where(self._edges.c.src.in_(frontier) | self._edges.c.dst.in_(frontier))
                results = conn.execute(q).fetchall()
                next_frontier: List[UUID] = []
                for src, dst in results:
                    next_frontier.extend([src, dst])
                # Fetch node details
                if next_frontier:
                    q_nodes = select(self._nodes).where(self._nodes.c.id.in_(next_frontier))
                    for row in conn.execute(q_nodes):
                        collected[row.id] = Node(
                            id=row.id,
                            label=row.label,
                            properties=row.properties or {},
                        )
                frontier = next_frontier
        # Also include initial nodes
        with self._engine.connect() as conn:
            q_init = select(self._nodes).where(self._nodes.c.id.in_(node_ids))
            for row in conn.execute(q_init):
                collected[row.id] = Node(
                    id=row.id,
                    label=row.label,
                    properties=row.properties or {},
                )
        return list(collected.values()) 