"""
Pydantic models for the Prompt service.

These models handle data validation and serialization for prompts
across both individual and organization hosting types.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PromptFile(BaseModel):
    """
    Model representing a prompt file discovered in a repository.
    Used by PromptDiscoveryService to represent YAML/YML prompt files.
    """
    path: str = Field(..., description="Full file path relative to repository")
    name: str = Field(..., description="File name")
    content: Optional[str] = Field(None, description="Full content of the file as JSON string")
    system_prompt: Optional[str] = Field(None, description="System prompt content")
    user_prompt: Optional[str] = Field(None, description="User prompt content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata from YAML")


class Prompt(BaseModel):
    """
    Core prompt model with all fields for database and API operations.
    """
    id: str = Field(..., description="Unique identifier for the prompt")
    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    content: str = Field(..., description="Full prompt content (JSON format)")
    repo_name: str = Field(..., description="Repository name where prompt is stored")
    file_path: str = Field(..., description="File path within the repository")
    category: Optional[str] = Field(None, description="Prompt category for organization")
    tags: List[str] = Field(default_factory=list, description="Tags for prompt categorization")
    system_prompt: Optional[str] = Field(None, description="System prompt content")
    user_prompt: Optional[str] = Field(None, description="User prompt content")
    owner: Optional[str] = Field(None, description="Owner username (for organization mode)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class PromptCreate(BaseModel):
    """
    Model for creating a new prompt.
    """
    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    repo_name: str = Field(..., description="Repository name where prompt will be stored")
    file_path: str = Field(..., description="File path within the repository")
    category: Optional[str] = Field(None, description="Prompt category")
    tags: List[str] = Field(default_factory=list, description="Tags for prompt")
    system_prompt: Optional[str] = Field(None, description="System prompt content")
    user_prompt: Optional[str] = Field(None, description="User prompt content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class PromptUpdate(BaseModel):
    """
    Model for updating an existing prompt.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = Field(None, description="Updated prompt name")
    description: Optional[str] = Field(None, description="Updated prompt description")
    category: Optional[str] = Field(None, description="Updated category")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    system_prompt: Optional[str] = Field(None, description="Updated system prompt")
    user_prompt: Optional[str] = Field(None, description="Updated user prompt")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class PromptList(BaseModel):
    """
    Response model for listing prompts.
    """
    prompts: List[Prompt] = Field(default_factory=list, description="List of prompts")
    total: int = Field(0, description="Total number of prompts")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page")


class PromptSearchParams(BaseModel):
    """
    Parameters for searching/filtering prompts.
    """
    query: Optional[str] = Field(default=None, description="Search query string")
    repo_name: Optional[str] = Field(default=None, description="Filter by repository name")
    category: Optional[str] = Field(default=None, description="Filter by category")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    owner: Optional[str] = Field(default=None, description="Filter by owner (organization mode)")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")