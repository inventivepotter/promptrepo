"""
Pydantic schemas for different message types used in agent conversations.

This module defines comprehensive models for:
- AI/Assistant messages
- User messages
- Tool call messages
- Tool response messages
- System messages
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class ToolCallSchema(BaseModel):
    """Schema for a tool call made by the AI."""
    
    id: str = Field(..., description="Unique identifier for this tool call")
    name: str = Field(..., description="Name of the tool being called")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool as key-value pairs"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "call_123abc",
                "name": "search_files",
                "arguments": {
                    "path": ".",
                    "regex": ".*\\.py$"
                }
            }
        }
    )


class BaseMessageSchema(BaseModel):
    """Base schema for all message types."""
    
    content: str = Field(..., description="The text content of the message")
    timestamp: Optional[datetime] = Field(
        default=None,
        description="When the message was created"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata associated with the message"
    )
    
    model_config = ConfigDict(extra="forbid")


class UserMessageSchema(BaseMessageSchema):
    """Schema for user messages."""
    
    role: Literal["user"] = Field(default="user", description="Message role - always 'user'")
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user who sent the message"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "Can you help me search for Python files?",
                "user_id": "user_123",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )


class AIMessageSchema(BaseMessageSchema):
    """Schema for AI/Assistant messages."""
    
    role: Literal["assistant"] = Field(
        default="assistant",
        description="Message role - always 'assistant'"
    )
    model: Optional[str] = Field(
        default=None,
        description="The AI model that generated this message"
    )
    tool_calls: Optional[List[ToolCallSchema]] = Field(
        default=None,
        description="Tool calls made by the assistant in this message"
    )
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter"]] = Field(
        default=None,
        description="Reason why the model stopped generating"
    )
    token_usage: Optional[Dict[str, int]] = Field(
        default=None,
        description="Token usage statistics for this message"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "role": "assistant",
                "content": "I'll search for Python files in the current directory.",
                "model": "claude-sonnet-4.5",
                "tool_calls": [
                    {
                        "id": "call_123",
                        "name": "search_files",
                        "arguments": {"path": ".", "regex": ".*\\.py$"}
                    }
                ],
                "finish_reason": "tool_calls",
                "token_usage": {
                    "input_tokens": 100,
                    "output_tokens": 50
                }
            }
        }
    )


class SystemMessageSchema(BaseMessageSchema):
    """Schema for system messages."""
    
    role: Literal["system"] = Field(
        default="system",
        description="Message role - always 'system'"
    )
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        default="medium",
        description="Priority level of the system message"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "role": "system",
                "content": "You are a helpful AI assistant specialized in code analysis.",
                "priority": "high",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )


class ToolMessageSchema(BaseMessageSchema):
    """Schema for tool result messages."""
    
    role: Literal["tool"] = Field(default="tool", description="Message role - always 'tool'")
    tool_call_id: str = Field(..., description="ID of the tool call this message responds to")
    tool_name: str = Field(..., description="Name of the tool that was executed")
    is_error: bool = Field(
        default=False,
        description="Whether the tool execution resulted in an error"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "role": "tool",
                "content": "Found 5 Python files: app.py, utils.py, models.py, services.py, tests.py",
                "tool_call_id": "call_123",
                "tool_name": "search_files",
                "is_error": False,
                "timestamp": "2024-01-15T10:30:05Z"
            }
        }
    )


# Union type for any message
MessageSchema = Union[
    UserMessageSchema,
    AIMessageSchema,
    SystemMessageSchema,
    ToolMessageSchema
]


class ConversationSchema(BaseModel):
    """Schema for a conversation containing multiple messages."""
    
    id: str = Field(..., description="Unique identifier for the conversation")
    messages: List[MessageSchema] = Field(
        default_factory=list,
        description="List of messages in the conversation"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user associated with this conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was last updated"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the conversation"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "conv_123",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": "Hello!",
                        "user_id": "user_123"
                    },
                    {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?",
                        "model": "claude-sonnet-4.5"
                    }
                ],
                "user_id": "user_123",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:10Z"
            }
        }
    )