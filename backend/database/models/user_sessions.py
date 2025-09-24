# models/user_sessions.py
from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlmodel import Session as DBSession, select
from sqlalchemy import DateTime
from datetime import datetime, timedelta, UTC
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from database.models.user import User


class UserSessions(SQLModel, table=True):
    __tablename__ = "user_sessions"  # type: ignore

    # Primary key as UUID
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    session_id: str = Field(
        unique=True, index=True, description="Session identifier sent to frontend"
    )
    oauth_token: str = Field(description="GitHub OAuth access token")

    # Relationship back to User
    user_id: str = Field(foreign_key="users.id", index=True)
    user: "User" = Relationship(back_populates="sessions")

    # Timestamps for tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime, default=func.now(), nullable=False  # Database default
        ),
    )
    accessed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime,
            default=func.now(),  # Initial value on insert
            onupdate=func.now(),  # Auto-update on row update
            nullable=False,
        ),
    )

    # Optional: Store minimal session data as JSON if needed
    data: Optional[str] = Field(
        default=None, description="JSON string for session metadata"
    )

    def __repr__(self) -> str:
        return f"<UserSessions(id={self.id}, session_id={self.session_id[:8]}..., user_id={self.user_id})>"

    def __str__(self) -> str:
        return f"Session {self.session_id[:8]}... for user {self.user_id}"
