from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
import uuid

from golett_core.settings import settings

__all__ = [
    "Document",
]


class Document(BaseModel):
    """Metadata about a user-provided document residing in the file store."""

    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    source_uri: str  # e.g., "s3://bucket/key.pdf"
    status: Literal["pending", "processing", "processed", "failed"] = "pending"

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
        json_schema_extra={
            "example": {
                "doc_id": "1afcc63f-e3bd-4d94-b2b0-e8f6b2306c90",
                "user_id": "user_123",
                "source_uri": "s3://my-bucket/documents/report.pdf",
                "status": "pending",
            }
        },
    ) 