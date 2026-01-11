"""
Model for shared chat sessions.
Stores chat sessions that users want to share via public links.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, UTC
from typing import Optional, Any
import uuid


class SharedChats(SQLModel, table=True):
    """Database model for shared chat sessions."""

    __tablename__ = "shared_chats"

    # Primary key as UUID
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )

    # Short, URL-safe identifier for public sharing
    share_id: str = Field(
        unique=True,
        index=True,
        description="Unique short ID for URL sharing"
    )

    # Chat metadata
    title: str = Field(
        max_length=255,
        description="Title of the chat session"
    )

    # Store messages as JSON
    messages: dict = Field(
        sa_column=Column(JSON, nullable=False),
        description="Full messages array serialized as JSON"
    )

    # Model configuration used for the chat
    model_config_data: dict = Field(
        sa_column=Column(JSON, nullable=False),
        description="Model configuration (provider, model, temperature, etc.)"
    )

    # Optional prompt metadata
    prompt_meta: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Prompt metadata (system prompt, tools, etc.)"
    )

    # Token and cost tracking
    total_tokens: int = Field(
        default=0,
        description="Total tokens used in session"
    )

    total_cost: float = Field(
        default=0.0,
        description="Total cost of session"
    )

    # Owner tracking (nullable for anonymous shares)
    created_by: Optional[str] = Field(
        default=None,
        index=True,
        description="User ID who created the share"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime, nullable=False)
    )

    # Optional expiration
    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=True),
        description="Optional expiration date for the share"
    )

    # Soft delete flag
    is_active: bool = Field(
        default=True,
        description="Whether the share is active"
    )

    def __repr__(self) -> str:
        return f"<SharedChats(id={self.id}, share_id={self.share_id}, title={self.title[:20]}...)>"

    def __str__(self) -> str:
        return f"SharedChat {self.share_id}: {self.title}"
