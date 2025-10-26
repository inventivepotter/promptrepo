"""
Pydantic models for the Prompt service.

These models handle data validation and serialization for prompts
across both individual and organization hosting types.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from services.local_repo.models import CommitInfo

class PromptData(BaseModel):
    """
    Core prompt data model with all fields that get saved to YAML files.
    This model represents the complete prompt configuration including LLM parameters.
    """
    id: str = Field(default="", description="Unique identifier for the prompt")
    name: str = Field(default="Untitled Prompt", description="Prompt name")
    description: Optional[str] = Field(default="", description="Prompt description")
    provider: str = Field(default="openai", description="LLM provider (e.g., openai, anthropic)")
    model: str = Field(default="gpt-4", description="Model name (e.g., gpt-4, claude-3)")
    failover_model: Optional[str] = Field(None, description="Backup model if primary fails")
    prompt: str = Field(default="", description="Combined prompt content")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice configuration")
    temperature: float = Field(..., ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(..., ge=0.0, le=1.0, description="Top-p sampling parameter")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format configuration")
    stream: Optional[bool] = Field(None, description="Whether to stream the response")
    n_completions: Optional[int] = Field(None, gt=0, description="Number of completions to generate")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    api_key: Optional[str] = Field(None, description="API key override")
    api_base: Optional[str] = Field(None, description="API base URL override")
    user: Optional[str] = Field(None, description="User identifier for tracking")
    parallel_tool_calls: Optional[bool] = Field(None, description="Enable parallel tool calls")
    logprobs: Optional[bool] = Field(None, description="Return log probabilities")
    top_logprobs: Optional[int] = Field(None, ge=0, le=20, description="Number of top log probabilities")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias adjustments")
    stream_options: Optional[Dict[str, Any]] = Field(None, description="Streaming options")
    max_completion_tokens: Optional[int] = Field(None, gt=0, description="Maximum completion tokens")
    reasoning_effort: Optional[Literal["minimal", "low", "medium", "high", "auto"]] = Field("auto", description="Reasoning effort level")
    extra_args: Optional[Dict[str, Any]] = Field(None, description="Additional provider-specific arguments")
    tags: List[str] = Field(default_factory=list, description="Tags for prompt categorization")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class PromptMeta(BaseModel):
    """
    Prompt metadata model that wraps PromptData with repository information.
    """
    prompt: PromptData = Field(..., description="Complete prompt data")
    recent_commits: Optional[List[CommitInfo]] = Field(None, description="Recent 5 commits for this prompt file")
    repo_name: str = Field(..., description="Repository name where prompt is stored")
    file_path: str = Field(..., description="File path within the repository")
    pr_info: Optional[Dict[str, Any]] = Field(None, description="Pull request information when applicable")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class PromptDataUpdate(BaseModel):
    """
    Partial model for updating prompt data.
    All fields from PromptData are optional to allow partial updates.
    This is essentially Partial<PromptData> for update operations.
    """
    id: Optional[str] = Field(None, description="Unique identifier for the prompt")
    name: Optional[str] = Field(None, description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    provider: Optional[str] = Field(None, description="LLM provider (e.g., openai, anthropic)")
    model: Optional[str] = Field(None, description="Model name (e.g., gpt-4, claude-3)")
    failover_model: Optional[str] = Field(None, description="Backup model if primary fails")
    prompt: Optional[str] = Field(None, description="Combined prompt content")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice configuration")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format configuration")
    stream: Optional[bool] = Field(None, description="Whether to stream the response")
    n_completions: Optional[int] = Field(None, gt=0, description="Number of completions to generate")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    api_key: Optional[str] = Field(None, description="API key override")
    api_base: Optional[str] = Field(None, description="API base URL override")
    user: Optional[str] = Field(None, description="User identifier for tracking")
    parallel_tool_calls: Optional[bool] = Field(None, description="Enable parallel tool calls")
    logprobs: Optional[bool] = Field(None, description="Return log probabilities")
    top_logprobs: Optional[int] = Field(None, ge=0, le=20, description="Number of top log probabilities")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias adjustments")
    stream_options: Optional[Dict[str, Any]] = Field(None, description="Streaming options")
    max_completion_tokens: Optional[int] = Field(None, gt=0, description="Maximum completion tokens")
    reasoning_effort: Optional[Literal["minimal", "low", "medium", "high", "auto"]] = Field(None, description="Reasoning effort level")
    extra_args: Optional[Dict[str, Any]] = Field(None, description="Additional provider-specific arguments")
    tags: Optional[List[str]] = Field(None, description="Tags for prompt categorization")