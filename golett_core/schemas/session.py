from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel, Field, ConfigDict
import uuid

from golett_core.settings import settings

__all__ = [
    "Session",
]


class Session(BaseModel):
    """Represents a single chat session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
        json_schema_extra={
            "example": {
                "session_id": "7f0e1d37-9f7c-47ad-8ba5-599946f77b87",
                "user_id": "user_123",
                "created_at": "2024-07-29T12:00:00Z",
                "session_metadata": {"channel": "web"},
            }
        },
    ) 