from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict
from services.prompt.models import PromptMeta
from schemas import MessageSchema


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions using PromptMeta"""
    prompt_meta: PromptMeta = Field(..., description="Prompt metadata with full configuration")
    messages: Optional[List[MessageSchema]] = Field(None, description="Optional conversation history")


class TokenUsage(BaseModel):
    """Token usage statistics from AgentTrace"""
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    total_tokens: int = Field(..., description="Total number of tokens")


class CostInfo(BaseModel):
    """Cost information from completion"""
    input_cost: float = Field(..., description="Cost for input tokens")
    output_cost: float = Field(..., description="Cost for output tokens")
    total_cost: float = Field(..., description="Total cost")


class ChatCompletionResponse(BaseModel):
    """Lightweight response model for chat completions"""
    content: str = Field(..., description="The generated completion content")
    finish_reason: Optional[str] = Field(None, description="Reason for completion finish (stop, length, tool_calls, etc.)")
    usage: Optional[TokenUsage] = Field(None, description="Token usage statistics")
    cost: Optional[CostInfo] = Field(None, description="Cost information")
    duration_ms: Optional[float] = Field(None, description="Inference duration in milliseconds")
    tool_calls: Optional[List[MessageSchema]] = Field(None, description="Tool calls and tool responses from the agent trace")
    messages: Optional[List[MessageSchema]] = Field(None, description="Full conversation history including the response")


# Schemas for LLM Providers endpoint
class ModelInfo(BaseModel):
    """Information about a specific model"""
    id: str
    name: str


class ProviderInfo(BaseModel):
    """Information about an LLM provider"""
    id: str
    name: str
    models: List[ModelInfo]


class ProvidersResponse(BaseModel):
    """Response for available providers endpoint"""
    providers: List[ProviderInfo]