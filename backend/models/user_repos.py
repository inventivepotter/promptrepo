# backend/models/user_repos.py
from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlalchemy import DateTime, Enum as SQLEnum
from datetime import datetime, UTC
from typing import Optional
from enum import Enum
import uuid


class RepoStatus(str, Enum):
    """Enumeration for repository clone status"""
    PENDING = "pending"
    CLONING = "cloning"
    CLONED = "cloned"
    FAILED = "failed"
    OUTDATED = "outdated"


class UserRepos(SQLModel, table=True):
    """
    Table to store user repository information and clone status.
    Links users to their repositories with clone URL and status tracking.
    """
    __tablename__ = "user_repos"
    __table_args__ = {'extend_existing': True}

    # Primary key as UUID
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Foreign key to users table
    user_id: str = Field(foreign_key="users.id", index=True, description="Reference to user ID")

    # Repository information
    repo_clone_url: str = Field(index=True, description="Git clone URL for the repository")
    repo_name: str = Field(index=True, description="Repository name (e.g., 'owner/repo-name')")

    # Clone status tracking
    status: RepoStatus = Field(
        default=RepoStatus.PENDING,
        sa_column=Column(SQLEnum(RepoStatus), nullable=False),
        description="Current clone status of the repository"
    )

    # Additional optional fields
    branch: Optional[str] = Field(default="main", description="Target branch to clone")
    local_path: Optional[str] = Field(default=None, description="Local file system path where repo is cloned")
    last_clone_attempt: Optional[datetime] = Field(default=None, description="Timestamp of last clone attempt")
    clone_error_message: Optional[str] = Field(default=None, description="Error message if clone failed")

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

    # Relationship back to User (if you want to access user from repo)
    # Uncomment the following lines if you want bidirectional relationship
    # user: Optional["User"] = Relationship(back_populates="repos")

    def __repr__(self) -> str:
        return f"<UserRepos(id={self.id}, user_id={self.user_id}, repo_name={self.repo_name}, status={self.status})>"

    def is_cloned_successfully(self) -> bool:
        """Check if repository is successfully cloned"""
        return self.status == RepoStatus.CLONED

    def is_clone_pending(self) -> bool:
        """Check if repository clone is pending"""
        return self.status == RepoStatus.PENDING

    def is_clone_failed(self) -> bool:
        """Check if repository clone failed"""
        return self.status == RepoStatus.FAILED

    def mark_as_cloning(self) -> None:
        """Mark repository as currently being cloned"""
        self.status = RepoStatus.CLONING
        self.last_clone_attempt = datetime.now(UTC)
        self.clone_error_message = None

    def mark_as_cloned(self, local_path: str) -> None:
        """Mark repository as successfully cloned"""
        self.status = RepoStatus.CLONED
        self.local_path = local_path
        self.clone_error_message = None

    def mark_as_failed(self, error_message: str) -> None:
        """Mark repository clone as failed"""
        self.status = RepoStatus.FAILED
        self.clone_error_message = error_message