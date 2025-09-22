"""
User table model
"""

from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlalchemy import DateTime
from datetime import datetime, UTC
from typing import Optional, List
import uuid
from database.models.user_repos import UserRepos
from database.models.user_sessions import UserSessions
from database.models.user_llm_configs import UserLLMConfigs


class User(SQLModel, table=True):
    """
    User table model representing authenticated users.
    """

    __tablename__ = "users"  # type: ignore

    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique user identifier",
    )

    # User information from OAuth provider (OAuth)
    oauth_provider: str = Field(
        index=True, description="OAuth provider, e.g., 'github'"
    )
    username: str = Field(index=True, unique=True, description="OAuth username")
    name: Optional[str] = Field(
        default=None, index=True, description="OAuth display name"
    )
    email: Optional[str] = Field(default=None, index=True, description="OAuth email")
    avatar_url: Optional[str] = Field(default=None, description="OAuth avatar URL")
    oauth_user_id: Optional[int] = Field(
        default=None, index=True, unique=True, description="OAuth user ID"
    )
    html_url: Optional[str] = Field(default=None, description="OAuth profile URL")

    # Relationships
    sessions: List["UserSessions"] = Relationship(back_populates="user")
    repos: List["UserRepos"] = Relationship(back_populates="user")
    llm_configs: List["UserLLMConfigs"] = Relationship(back_populates="user")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime, default=func.now(), nullable=False),
        description="When the user was created",
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime, default=func.now(), onupdate=func.now(), nullable=False
        ),
        description="When the user was last modified",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"

    def __str__(self) -> str:
        return self.username or self.id
