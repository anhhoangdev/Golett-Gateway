import os
from typing import List, Optional
from uuid import UUID

from sqlalchemy import create_engine, Column, String, JSON, DateTime, text, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

from golett_core.schemas import Session, ChatMessage
from golett_core.interfaces import (
    SessionStoreInterface, 
    HistoryStoreInterface, 
    MemoryInterface
)
from golett_core.schemas.memory import ContextBundle


Base = declarative_base()

class SessionModel(Base):
    __tablename__ = 'sessions'
    session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=UUID)
    user_id: Mapped[Optional[str]] = mapped_column(String(255))
    session_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatMessageModel(Base):
    __tablename__ = 'chat_messages'
    message_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=UUID)
    session_id: Mapped[UUID] = mapped_column(ForeignKey('sessions.session_id'))
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresMemoryStore(SessionStoreInterface, HistoryStoreInterface, MemoryInterface):
    def __init__(self, dsn: Optional[str] = None):
        if dsn is None:
            dsn = os.getenv("POSTGRES_DSN")
            if not dsn:
                raise ValueError("PostgreSQL DSN must be provided via argument or POSTGRES_DSN env var")
        self.engine = create_engine(dsn)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        with self.SessionLocal() as db:
            session_model = db.get(SessionModel, session_id)
            if session_model:
                return Session.model_validate(session_model.__dict__)
        return None

    async def create_session(self, session: Session) -> Session:
        with self.SessionLocal() as db:
            new_session_model = SessionModel(**session.model_dump())
            db.add(new_session_model)
            db.commit()
            db.refresh(new_session_model)
            return Session.model_validate(new_session_model.__dict__)

    async def get_recent_messages(self, session_id: UUID, limit: int = 20) -> List[ChatMessage]:
        """Return the `limit` most-recent messages for *session_id* (oldest first)."""
        with self.SessionLocal() as db:
            rows = (
                db.query(ChatMessageModel)
                .filter(ChatMessageModel.session_id == session_id)
                .order_by(ChatMessageModel.created_at.desc())
                .limit(limit)
                .all()
            )

            # Convert SQLAlchemy rows ➜ Pydantic ChatMessage (reverse to chronological)
            return [
                ChatMessage(
                    id=row.message_id,
                    session_id=row.session_id,
                    role=row.role,
                    content=row.content,
                    created_at=row.created_at,
                )
                for row in reversed(rows)
            ]

    async def create_message(self, session_id: UUID, message: ChatMessage) -> None:
        """Persist *message* (belonging to *session_id*) in the database."""
        payload = message.model_dump(exclude={"id", "session_id", "embedding"})

        with self.SessionLocal() as db:
            # Ensure session row exists to satisfy FK constraint
            if db.get(SessionModel, session_id) is None:
                db.add(
                    SessionModel(
                        session_id=session_id,
                        user_id="anonymous",
                    )
                )
                db.flush()

            new_message_model = ChatMessageModel(
                message_id=message.id,
                session_id=session_id,
                **payload,
            )
            db.add(new_message_model)
            db.commit()

    async def save_message(self, msg: ChatMessage) -> None:
        """Saves a message to memory."""
        # Map to DB record via create_message.
        await self.create_message(msg.session_id, msg)

    async def search(
        self, session_id: UUID, query: str, include_recent: bool = True
    ) -> ContextBundle:
        """
        Searches memory to build a context bundle for a query.
        """
        recent_messages = await self.get_recent_messages(session_id)
        return ContextBundle(
            recalled_context=None,
            related_context=[],
            recent_context=recent_messages
        ) 