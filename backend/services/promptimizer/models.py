"""
Pydantic models for the Promptimizer service.

This module defines request and response models for prompt optimization.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

from schemas.messages import MessageSchema


class PromptOptimizerRequest(BaseModel):
    """Request model for prompt optimization."""

    idea: str = Field(
        ...,
        description="User's idea or description for the prompt to be generated/enhanced",
        min_length=1
    )
    provider: str = Field(
        ...,
        description="Target LLM provider (e.g., 'openai', 'anthropic', 'google')"
    )
    model: str = Field(
        ...,
        description="Target model name (e.g., 'gpt-4', 'claude-3-opus')"
    )
    expects_user_message: bool = Field(
        default=False,
        description="Whether the prompt will receive user messages (adds security guardrails if True)"
    )
    conversation_history: Optional[List[MessageSchema]] = Field(
        default=None,
        description="Previous conversation history for multi-turn optimization"
    )
    current_prompt: Optional[str] = Field(
        default=None,
        description="Current prompt content to be enhanced (if user wants to improve existing prompt)"
    )


class PromptOptimizerResponse(BaseModel):
    """Response model for prompt optimization."""

    optimized_prompt: str = Field(
        ...,
        description="The enhanced/optimized system prompt"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Brief explanation of optimizations made (if requested)"
    )
