# models/user_sessions.py
from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlmodel import Session as DBSession, select
from sqlalchemy import DateTime
from datetime import datetime, timedelta, UTC
from typing import Optional, List
import uuid
from settings import base_settings


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Add this line

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True, description="GitHub username")
    name: Optional[str] = Field(index=True, description="GitHub display name")
    email: Optional[str] = Field(index=True, description="GitHub email")
    avatar_url: Optional[str] = Field(description="GitHub avatar URL")
    github_id: Optional[int] = Field(index=True, description="GitHub user ID")
    html_url: Optional[str] = Field(description="GitHub profile URL")
    sessions: List["User_Sessions"] = Relationship(back_populates="user")


    #Timestamps for tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC),
                                 sa_column=Column(DateTime,
                                     default=func.now(),  # Database default
                                     nullable=False
                                 )
                                 )
    modified_at: datetime = Field(default_factory=lambda: datetime.now(UTC),
                                  sa_column=Column(DateTime,
                                      default=func.now(),  # Initial value on insert
                                      onupdate=func.now(),  # Auto-update on row update
                                      nullable=False)
                                  )



class User_Sessions(SQLModel, table=True):
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}  # Add this line


    # Primary key as UUID
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # The three core fields you want
    username: str = Field(foreign_key="users.username", index=True, description="GitHub username")
    session_id: str = Field(unique=True, index=True, description="Session identifier sent to frontend")
    oauth_token: str = Field(description="GitHub OAuth access token")
    
    # Relationship back to User
    user: Optional["User"] = Relationship(back_populates="sessions")
    # Timestamps for tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC),
                                 sa_column=Column(DateTime,
                                     default=func.now(),  # Database default
                                     nullable=False
                                 )
                                 )
    accessed_at: datetime = Field(default_factory=lambda: datetime.now(UTC),
                                  sa_column=Column(DateTime,
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
        statement = select(cls).where(cls.accessed_at < expiration_time)
        expired_sessions = db.exec(statement).all()
        for session in expired_sessions:
            db.delete(session)
        db.commit()
        return len(expired_sessions)
