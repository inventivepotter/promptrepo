"""
Models for conversational services.

Defines request/response models for conversation simulation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from services.artifacts.evals.models import Turn


class SimulateConversationRequest(BaseModel):
    """Request model for simulating a conversation based on user goal."""

    # Prompt configuration
    prompt_reference: str = Field(
        description="Reference to the prompt file being tested"
    )

    # User persona/goal for simulation
    user_goal: str = Field(
        description="Goal for the simulated user (e.g., 'Get help with order refund')"
    )
    user_persona: Optional[str] = Field(
        default=None,
        description="Persona description for the simulated user (e.g., 'Frustrated customer')"
    )

    # Generation parameters
    min_turns: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Minimum number of conversation turns"
    )
    max_turns: int = Field(
        default=6,
        ge=1,
        le=20,
        description="Maximum number of conversation turns"
    )
    stopping_criteria: Optional[str] = Field(
        default=None,
        description="When to stop the conversation (e.g., 'When user's concern is resolved')"
    )

    # Template variables for the prompt
    template_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables to apply to the prompt"
    )

    # LLM configuration for user simulation (optional - uses prompt's config if not provided)
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider for simulation (uses prompt's config if not provided)"
    )
    model: Optional[str] = Field(
        default=None,
        description="LLM model for simulation (uses prompt's config if not provided)"
    )


class SimulateConversationResponse(BaseModel):
    """Response model for simulated conversation."""

    turns: List[Turn] = Field(
        description="Simulated conversation turns"
    )
    goal_achieved: bool = Field(
        default=False,
        description="Whether the simulation determined the goal was achieved"
    )
    stopping_reason: Optional[str] = Field(
        default=None,
        description="Reason why the simulation stopped"
    )
