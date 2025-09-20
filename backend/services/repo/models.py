"""
Repo Data Models

This module contains Pydantic models for all Repo-related data structures,
ensuring type safety and consistent data validation across the Repo service.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PromptFile(BaseModel):
    """Represents a prompt file found in a repository."""
    path: str
    name: str
    content: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None


class UserCredentials(BaseModel):
    """Represents user credentials for repository operations."""
    username: str
    token: str


class CommitInfo(BaseModel):
    """Represents information about a commit."""
    commit_id: str
    message: str
    author: str
    timestamp: datetime