"""
User table model
"""

from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlalchemy import DateTime, Index
from datetime import datetime, UTC
from typing import Optional, List
import uuid
from database.models.user_repos import UserRepos
from database.models.user_sessions import UserSessions
from database.models.user_llm_configs import UserLLMConfigs
from services.oauth.enums import OAuthProvider


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
    oauth_provider: OAuthProvider = Field(
        index=True, description="OAuth provider, e.g., 'github'"
    )
    oauth_username: str = Field(index=True, description="OAuth username")
    oauth_name: Optional[str] = Field(
        default=None, description="OAuth display name"
    )
    oauth_email: Optional[str] = Field(default=None, description="OAuth email")
    oauth_avatar_url: Optional[str] = Field(default=None, description="OAuth avatar URL")
    oauth_user_id: Optional[str] = Field(
        default=None, description="OAuth user ID"
    )
    oauth_profile_url: Optional[str] = Field(default=None, description="OAuth profile URL")

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
        return f"<User(id={self.id}, oauth_username={self.oauth_username}, oauth_provider={self.oauth_provider})>"

    def __str__(self) -> str:
        return f"{self.oauth_username} ({self.oauth_provider})"
