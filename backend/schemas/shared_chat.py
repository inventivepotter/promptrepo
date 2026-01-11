"""
Pydantic schemas for shared chat functionality.
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class SharedChatTokenUsage(BaseModel):
    """Token usage statistics for a message."""

    prompt_tokens: Optional[int] = Field(default=None, description="Input tokens")
    completion_tokens: Optional[int] = Field(default=None, description="Output tokens")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens")
    reasoning_tokens: Optional[int] = Field(default=None, description="Reasoning tokens")

    model_config = ConfigDict(extra="ignore")


class SharedChatToolCall(BaseModel):
    """Tool call made by the assistant."""

    id: str = Field(..., description="Tool call identifier")
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments"
    )

    model_config = ConfigDict(extra="ignore")


class SharedChatMessage(BaseModel):
    """Message structure for shared chat storage."""

    id: str = Field(..., description="Message identifier")
    role: Literal["user", "assistant", "system", "tool"] = Field(
        ...,
        description="Message role"
    )
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was created")
    usage: Optional[SharedChatTokenUsage] = Field(
        default=None,
        description="Token usage for this message"
    )
    cost: Optional[float] = Field(default=None, description="Cost for this message")
    inference_time_ms: Optional[float] = Field(
        default=None,
        description="Inference time in milliseconds"
    )
    tool_calls: Optional[List[SharedChatToolCall]] = Field(
        default=None,
        description="Tool calls made in this message"
    )

    model_config = ConfigDict(extra="ignore")


class SharedChatModelConfig(BaseModel):
    """Model configuration for shared chat."""

    provider: str = Field(..., description="LLM provider name")
    model: str = Field(..., description="Model identifier")
    temperature: Optional[float] = Field(default=None, description="Temperature setting")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens setting")

    model_config = ConfigDict(extra="ignore")


class CreateSharedChatRequest(BaseModel):
    """Request to create a shared chat."""

    title: str = Field(..., description="Chat session title", max_length=255)
    messages: List[SharedChatMessage] = Field(
        ...,
        description="Messages in the chat session"
    )
    model_config_data: SharedChatModelConfig = Field(
        ...,
        description="Model configuration used"
    )
    prompt_meta: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Prompt metadata"
    )
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_cost: float = Field(default=0.0, description="Total cost")

    model_config = ConfigDict(extra="forbid")


class SharedChatResponse(BaseModel):
    """Response containing shared chat data."""

    id: str = Field(..., description="Database ID")
    share_id: str = Field(..., description="Share URL identifier")
    title: str = Field(..., description="Chat title")
    messages: List[SharedChatMessage] = Field(..., description="Chat messages")
    model_config_data: SharedChatModelConfig = Field(
        ...,
        description="Model configuration"
    )
    prompt_meta: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Prompt metadata"
    )
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")
    created_at: datetime = Field(..., description="When the share was created")

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CreateSharedChatResponse(BaseModel):
    """Response after creating a shared chat."""

    share_id: str = Field(..., description="The share identifier for URL")
    share_url: str = Field(..., description="Full shareable URL")

    model_config = ConfigDict(extra="forbid")


class SharedChatListItem(BaseModel):
    """List item for user's shared chats."""

    id: str = Field(..., description="Database ID")
    share_id: str = Field(..., description="Share URL identifier")
    title: str = Field(..., description="Chat title")
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")
    created_at: datetime = Field(..., description="When the share was created")
    message_count: int = Field(..., description="Number of messages")

    model_config = ConfigDict(from_attributes=True, extra="ignore")
