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

    def __init__(self, **kwargs):
        if "session_key" not in kwargs:
            kwargs["session_key"] = self.generate_session_key()
        super().__init__(**kwargs)

    @staticmethod
    def generate_session_key() -> str:
        """Generate a secure random session key"""
        return str(uuid.uuid4()).replace("-", "")

    @classmethod
    def delete_expired(cls, db: DBSession, ttl: timedelta):
        """
        Delete sessions older than the given TTL.

        Args:
            db: SQLModel database session
            ttl: timedelta after which sessions are considered expired
        """
        expiration_time = datetime.now(UTC) - ttl
        statement = select(cls).where(cls.accessed_at < expiration_time)
        expired_sessions = db.exec(statement).all()
        for session in expired_sessions:
            db.delete(session)
        db.commit()
        return len(expired_sessions)

    def is_expired(self, ttl_seconds: int) -> bool:
        """
        Check if the session is expired based on the time-to-live (TTL).

        Args:
            ttl_seconds: Time-to-live in seconds.

        Returns:
            True if the session is expired, False otherwise.
        """
        expiration_time = datetime.now(UTC) - timedelta(seconds=ttl_seconds)
        return self.accessed_at < expiration_time
