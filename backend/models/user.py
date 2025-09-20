"""
User table model
"""
from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlalchemy import DateTime
from datetime import datetime, UTC
from typing import Optional, List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from models.user_repos import UserRepos
    from models.user_sessions import UserSessions
    from models.user_llm_configs import UserLLMConfigs


class User(SQLModel, table=True):
    """
    User table model representing authenticated users.
    """
    __tablename__ = "users"  # type: ignore
    
    
    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique user identifier"
    )
    
    # User information from OAuth provider (GitHub)
    username: str = Field(
        index=True,
        unique=True,
        description="GitHub username"
    )
    name: Optional[str] = Field(
        default=None,
        index=True,
        description="GitHub display name"
    )
    email: Optional[str] = Field(
        default=None,
        index=True,
        description="GitHub email"
    )
    avatar_url: Optional[str] = Field(
        default=None,
        description="GitHub avatar URL"
    )
    github_id: Optional[int] = Field(
        default=None,
        index=True,
        unique=True,
        description="GitHub user ID"
    )
    html_url: Optional[str] = Field(
        default=None,
        description="GitHub profile URL"
    )
    
    # Relationships
    sessions: List["models.user_sessions.UserSessions"] = Relationship(back_populates="user")
    repos: List["models.user_repos.UserRepos"] = Relationship(back_populates="user")
    llm_configs: List["models.user_llm_configs.UserLLMConfigs"] = Relationship(back_populates="user")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime,
            default=func.now(),
            nullable=False
        ),
        description="When the user was created"
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime,
            default=func.now(),
            onupdate=func.now(),
            nullable=False
        ),
        description="When the user was last modified"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
    
    def __str__(self) -> str:
        return self.username or self.id