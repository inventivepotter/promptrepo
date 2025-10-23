"""
Repo Data Models

This module contains Pydantic database.models for all Repo-related data structures,
ensuring type safety and consistent data validation across the Repo service.
"""

from typing import List, Optional
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

class UserOAuthDetails(BaseModel):
    """Pydantic model for user OAuth information."""
    oauth_provider: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_username: Optional[str] = None


class RepoInfo(BaseModel):
    id: str
    name: str
    full_name: str
    clone_url: str
    owner: str
    private: bool = False
    default_branch: str = "main"
    language: Optional[str] = None
    size: int = 0
    updated_at: Optional[str] = None
    all_branches: Optional[List[str]] = None


class RepositoryList(BaseModel):
    """Pydantic model for a list of repositories."""
    repositories: List[RepoInfo]


class BranchInfo(BaseModel):
    """Information about a repository branch"""
    name: str
    is_default: bool = False


class RepositoryBranchesResponse(BaseModel):
    """Response containing repository branches"""
    branches: List[BranchInfo]
    default_branch: str


class PullRequestInfo(BaseModel):
    """Information about a pull request"""
    pr_number: int
    pr_url: str
    pr_id: int
    title: str
    state: str
    head_branch: str
    base_branch: str
    is_draft: bool = False


class PullRequestResult(BaseModel):
    """Result of a pull request operation"""
    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    pr_id: Optional[int] = None
    error: Optional[str] = None
    data: Optional[dict] = None