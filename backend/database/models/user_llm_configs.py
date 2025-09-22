# backend/models/user_llm_configs.py
from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlalchemy import DateTime, Text
from datetime import datetime, UTC
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from database.models.user import User


class UserLLMConfigs(SQLModel, table=True):
    """
    Table to store user-specific LLM configurations.
    Links users to their preferred LLM settings.
    """
    __tablename__ = "user_llm_configs"  # type: ignore[assignment]

    # Primary key as UUID
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Foreign key to users table
    user_id: str = Field(foreign_key="users.id", index=True, description="Reference to user ID")

    # LLM Configuration
    provider: str = Field(index=True, description="LLM provider (e.g., 'openai', 'anthropic', 'google')")
    model_name: str = Field(index=True, description="Specific model name (e.g., 'gpt-4', 'claude-3-opus')")
    api_key: Optional[str] = Field(default=None, sa_column=Column(Text), description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Custom base URL for the LLM API")

    # Timestamps for tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime, default=func.now(), nullable=False),
        description="When this record was created"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False),
        description="When this record was last updated"
    )

    # Relationship back to User
    user: Optional["User"] = Relationship(back_populates="llm_configs")

    def __repr__(self) -> str:
        return f"<UserLLMConfigs(id={self.id}, user_id={self.user_id}, provider={self.provider}, model_name={self.model_name})>"
