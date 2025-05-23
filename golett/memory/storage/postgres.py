import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid

try:
    import psycopg2
    from psycopg2.extras import Json, RealDictCursor
except ImportError:
    raise ImportError(
        "PostgreSQL support requires psycopg2. "
        "Please install it with: pip install psycopg2-binary"
    )

from golett.memory.storage.interface import BaseMemoryStorage
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class PostgresMemoryStorage(BaseMemoryStorage):
    """
    PostgreSQL implementation for storing structured memory data.
    
    This class stores BI-related structured information and chat history
    in a PostgreSQL database for efficient retrieval and querying.
    """

    def __init__(
        self,
        connection_string: str,
        table_name: str = "golett_memories",
        schema: str = "public",
    ) -> None:
        """
        Initialize the PostgreSQL storage.
        
        Args:
            connection_string: PostgreSQL connection string 
            table_name: Name of the table to store memories in
            schema: Database schema to use
        """
        self.connection_string = connection_string
        self.table_name = table_name
        self.schema = schema
        self.initialize()

    def _get_connection(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            return psycopg2.connect(self.connection_string)
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise

    def initialize(self) -> None:
        """
        Initialize the PostgreSQL database and create necessary tables.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create the schema if it doesn't exist (if not public)
                    if self.schema != "public":
                        cursor.execute(
                            f"CREATE SCHEMA IF NOT EXISTS {self.schema}"
                        )
                    
                    # Create the memories table if it doesn't exist
                    cursor.execute(
                        f"""
                        CREATE TABLE IF NOT EXISTS {self.schema}.{self.table_name} (
                            id VARCHAR(36) PRIMARY KEY,
                            key VARCHAR(255) NOT NULL,
                            data JSONB NOT NULL,
                            metadata JSONB,
                            created_at TIMESTAMP NOT NULL,
                            updated_at TIMESTAMP NOT NULL,
                            session_id VARCHAR(36),
                            importance REAL DEFAULT 0.5
                        )
                        """
                    )
                    
                    # Create indexes for faster queries
                    cursor.execute(
                        f"""
                        CREATE INDEX IF NOT EXISTS idx_{self.table_name}_key 
                        ON {self.schema}.{self.table_name} (key)
                        """
                    )
                    
                    cursor.execute(
                        f"""
                        CREATE INDEX IF NOT EXISTS idx_{self.table_name}_session 
                        ON {self.schema}.{self.table_name} (session_id)
                        """
                    )
                    
                    cursor.execute(
                        f"""
                        CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created 
                        ON {self.schema}.{self.table_name} (created_at DESC)
                        """
                    )
                    
                conn.commit()
                logger.info(f"PostgreSQL memory storage initialized: {self.schema}.{self.table_name}")
        except psycopg2.Error as e:
            logger.error(f"Error during database initialization: {e}")
            raise

    def save(self, key: str, data: Any, metadata: Dict[str, Any]) -> str:
        """
        Save data to the PostgreSQL storage.
        
        Args:
            key: Unique identifier for this memory entry
            data: The data to be stored (will be converted to JSON)
            metadata: Additional context information
            
        Returns:
            The ID of the saved entry
        """
        try:
            entry_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            session_id = metadata.get("session_id", None)
            importance = metadata.get("importance", 0.5)
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                        INSERT INTO {self.schema}.{self.table_name} 
                        (id, key, data, metadata, created_at, updated_at, session_id, importance)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            entry_id, 
                            key, 
                            Json(data if isinstance(data, dict) else {"content": data}),
                            Json(metadata),
                            now,
                            now,
                            session_id,
                            importance
                        ),
                    )
                conn.commit()
                logger.debug(f"Saved memory with key: {key}, id: {entry_id}")
                return entry_id
        except psycopg2.Error as e:
            logger.error(f"Error saving to memory storage: {e}")
            raise

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific memory entry by key.
        
        Args:
            key: The identifier of the memory to retrieve
            
        Returns:
            The memory entry if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        f"""
                        SELECT * FROM {self.schema}.{self.table_name}
                        WHERE key = %s
                        ORDER BY updated_at DESC
                        LIMIT 1
                        """,
                        (key,),
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        return dict(row)
            return None
        except psycopg2.Error as e:
            logger.error(f"Error loading from memory storage: {e}")
            return None

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Alias for load method for compatibility.
        
        Args:
            key: The identifier of the memory to retrieve
            
        Returns:
            The memory entry if found, None otherwise
        """
        return self.load(key)

    def search(self, query: Any, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for relevant memory entries.
        
        Args:
            query: The search query (can be a string or dict)
            limit: Maximum number of results to return
            **kwargs: Additional search parameters including:
                - session_id: Filter by session
                - start_date: Filter by date range start
                - end_date: Filter by date range end
                - importance_threshold: Minimum importance score
                
        Returns:
            List of matching memory entries
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    where_clauses = []
                    params = []
                    
                    # Handle text search
                    if isinstance(query, str) and query:
                        where_clauses.append("(data::text ILIKE %s OR metadata::text ILIKE %s)")
                        search_pattern = f"%{query}%"
                        params.extend([search_pattern, search_pattern])
                    
                    # Handle dictionary search
                    elif isinstance(query, dict) and query:
                        for k, v in query.items():
                            # Search in data
                            where_clauses.append(f"(data->>%s = %s)")
                            params.extend([k, str(v)])
                    
                    # Additional filters from kwargs
                    if "session_id" in kwargs and kwargs["session_id"]:
                        where_clauses.append("session_id = %s")
                        params.append(kwargs["session_id"])
                        
                    if "start_date" in kwargs and kwargs["start_date"]:
                        where_clauses.append("created_at >= %s")
                        params.append(kwargs["start_date"])
                        
                    if "end_date" in kwargs and kwargs["end_date"]:
                        where_clauses.append("created_at <= %s")
                        params.append(kwargs["end_date"])
                        
                    if "importance_threshold" in kwargs:
                        where_clauses.append("importance >= %s")
                        params.append(float(kwargs["importance_threshold"]))
                    
                    # Construct the query
                    sql_query = f"SELECT * FROM {self.schema}.{self.table_name}"
                    if where_clauses:
                        sql_query += " WHERE " + " AND ".join(where_clauses)
                    
                    sql_query += " ORDER BY importance DESC, created_at DESC LIMIT %s"
                    params.append(limit)
                    
                    cursor.execute(sql_query, params)
                    rows = cursor.fetchall()
                    
                    return [dict(row) for row in rows] if rows else []
        except psycopg2.Error as e:
            logger.error(f"Error searching in memory storage: {e}")
            return []

    def delete(self, key: str) -> bool:
        """
        Delete a specific memory entry.
        
        Args:
            key: The identifier of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                        DELETE FROM {self.schema}.{self.table_name}
                        WHERE key = %s
                        """,
                        (key,),
                    )
                    rows_deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Deleted {rows_deleted} memory entries with key: {key}")
                return rows_deleted > 0
        except psycopg2.Error as e:
            logger.error(f"Error deleting from memory storage: {e}")
            return False

    def reset(self) -> None:
        """Reset/clear all data from storage."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"TRUNCATE TABLE {self.schema}.{self.table_name}"
                    )
                conn.commit()
                logger.info(f"Reset memory storage: {self.schema}.{self.table_name}")
        except psycopg2.Error as e:
            logger.error(f"Error resetting memory storage: {e}")
            raise
            
    def get_session_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a specific session.
        
        Args:
            session_id: The session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation entries in chronological order
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        f"""
                        SELECT * FROM {self.schema}.{self.table_name}
                        WHERE session_id = %s
                        ORDER BY created_at ASC
                        LIMIT %s
                        """,
                        (session_id, limit),
                    )
                    rows = cursor.fetchall()
                    
                    return [dict(row) for row in rows] if rows else []
        except psycopg2.Error as e:
            logger.error(f"Error retrieving session history: {e}")
            return [] 