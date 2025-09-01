from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict, Union


class ChatMessage(BaseModel):
    """OpenAI-compatible message format"""
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions"""
    messages: List[ChatMessage]
    provider: str = Field(..., description="LLM provider (e.g., openai, mistral, anthropic)")
    model: str = Field(..., description="Model name (e.g., gpt-3.5-turbo, claude-3)")
    prompt_id: Optional[str] = Field(None, description="Optional prompt ID for context")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")


class PromptTokensDetails(BaseModel):
    """Breakdown of tokens used in the prompt"""
    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None

class CompletionTokensDetails(BaseModel):
    """Breakdown of tokens used in a completion"""
    accepted_prediction_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None

class UsageStats(BaseModel):
    """Usage statistics for chat completion"""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None
    completion_tokens_details: Optional[CompletionTokensDetails] = None


class ChatCompletionChoice(BaseModel):
    """Choice in chat completion response"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """Response model for chat completions"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[UsageStats] = None


class ChatCompletionStreamChoice(BaseModel):
    """Choice in streaming chat completion response"""
    index: int
    delta: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    """Streaming response model for chat completions"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]


class ErrorResponse(BaseModel):
    """Error response model"""
    error: Dict[str, Any]