"""
Git Service Data Models

This module contains Pydantic database.models for all Git-related data structures,
ensuring type safety and consistent data validation across the Git service.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class GitOperationResult(BaseModel):
    """Represents the result of a Git operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class PullRequestResult(BaseModel):
    """Represents the result of a pull request creation."""
    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    pr_id: Optional[int] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class RepoStatus(BaseModel):
    """Represents the status of a repository."""
    current_branch: str
    is_dirty: bool
    untracked_files: List[str]
    modified_files: List[str]
    staged_files: List[str]
    commits_ahead: int
    last_commit: Dict[str, Any]
    error: Optional[str] = None


class CommitInfo(BaseModel):
    """Represents information about a commit."""
    commit_id: str
    message: str
    author: str
    timestamp: datetime