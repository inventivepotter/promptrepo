"""
Pydantic database.models for user service responses.
"""
from typing import Dict
from pydantic import BaseModel, Field
from database.models import RepoStatus


class RepositoryStatusCount(BaseModel):
    """Model for repository status count response."""
    status_counts: Dict[RepoStatus, int] = Field(..., description="Count of repositories by status")