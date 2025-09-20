# backend/schemas/user_repos.py
"""
Pydantic schemas for user repositories API endpoints.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from models.user_repos import UserRepos, RepoStatus


class AddRepositoryRequest(BaseModel):
    """Request schema for adding a new repository."""
    repo_clone_url: str = Field(..., description="Git clone URL for the repository")
    repo_name: str = Field(..., description="Repository name (e.g., 'owner/repo-name')")
    branch: Optional[str] = Field(default="main", description="Target branch to clone")


class UpdateRepositoryStatusRequest(BaseModel):
    """Request schema for updating repository status."""
    status: RepoStatus = Field(..., description="New repository status")
    local_path: Optional[str] = Field(default=None, description="Local path (for successful clones)")
    error_message: Optional[str] = Field(default=None, description="Error message (for failed clones)")


class UserRepositoryResponse(BaseModel):
    """Response schema for a single user repository."""
    id: str = Field(..., description="Repository ID")
    user_id: str = Field(..., description="User ID who owns this repository")
    repo_clone_url: str = Field(..., description="Git clone URL")
    repo_name: str = Field(..., description="Repository name")
    status: RepoStatus = Field(..., description="Current clone status")
    branch: Optional[str] = Field(description="Target branch")
    local_path: Optional[str] = Field(description="Local file system path")
    last_clone_attempt: Optional[datetime] = Field(description="Last clone attempt timestamp")
    clone_error_message: Optional[str] = Field(description="Error message if clone failed")
    created_at: datetime = Field(..., description="When the record was created")
    updated_at: datetime = Field(..., description="When the record was last updated")

    class Config:
        from_attributes = True


class UserRepositoriesResponse(BaseModel):
    """Response schema for multiple user repositories."""
    repositories: List[UserRepositoryResponse] = Field(..., description="List of user repositories")
    total_count: int = Field(..., description="Total number of repositories")


class RepositoryStatusSummary(BaseModel):
    """Summary of repository counts by status."""
    pending: int = Field(default=0, description="Number of pending repositories")
    cloning: int = Field(default=0, description="Number of repositories being cloned")
    cloned: int = Field(default=0, description="Number of successfully cloned repositories")
    failed: int = Field(default=0, description="Number of failed clone attempts")
    outdated: int = Field(default=0, description="Number of outdated repositories")


class UserRepositoriesSummaryResponse(BaseModel):
    """Response schema for user repositories summary."""
    user_id: str = Field(..., description="User ID")
    status_summary: RepositoryStatusSummary = Field(..., description="Count by status")
    total_repositories: int = Field(..., description="Total number of repositories")


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")