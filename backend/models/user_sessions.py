# models/user_sessions.py
from sqlmodel import SQLModel, Field, Column, func
from sqlmodel import Session as DBSession, select
from datetime import datetime, timedelta, UTC
from typing import Optional
import uuid
from backend.settings import base_settings


class User_Sessions(SQLModel, table=True):
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}  # Add this line


    # Primary key as UUID
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # The three core fields you want
    username: str = Field(index=True, description="GitHub username")
    session_id: str = Field(unique=True, index=True, description="Session identifier sent to frontend")
    oauth_token: str = Field(description="GitHub OAuth access token")

    # Timestamps for tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC),
                                 sa_column=Column(
                                     default=func.now(),  # Database default
                                     nullable=False
                                 )
                                 )
    modified_at: datetime = Field(default_factory=lambda: datetime.now(UTC),
                                  sa_column=Column(
                                      default=func.now(),  # Initial value on insert
                                      onupdate=func.now(),  # Auto-update on row update
                                      nullable=False)
                                  )

    # Optional: Store minimal session data as JSON if needed
    data: Optional[str] = Field(default=None, description="JSON string for session metadata")

    def __init__(self, **kwargs):
        if 'session_key' not in kwargs:
            kwargs['session_key'] = self.generate_session_key()
        super().__init__(**kwargs)

    @staticmethod
    def generate_session_key() -> str:
        """Generate a secure random session key"""
        return str(uuid.uuid4()).replace('-', '')

    @classmethod
    def delete_expired(cls, db: DBSession, ttl: timedelta):
        """
        Delete sessions older than the given TTL.

        Args:
            db: SQLModel database session
            ttl: timedelta after which sessions are considered expired
        """
        expiration_time = datetime.now(UTC) - ttl
        statement = select(cls).where(cls.modified_at < expiration_time)
        expired_sessions = db.exec(statement).all()
        for session in expired_sessions:
            db.delete(session)
        db.commit()
        return len(expired_sessions)  # Return how many were deleted
