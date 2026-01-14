"""
API endpoints for conversation simulation.

Provides endpoints for simulating conversations based on user goals.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

from api.deps import (
    CurrentUserDep,
    ConversationSimulatorServiceDep,
)
from middlewares.rest.responses import StandardResponse
from services.conversational.models import (
    SimulateConversationRequest,
    SimulateConversationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ==============================================================================
# Request/Response Models for API
# ==============================================================================

class SimulateConversationApiRequest(BaseModel):
    """API request model for simulating a conversation."""

    repo_name: str = Field(description="Repository name")
    prompt_reference: str = Field(description="Reference to the prompt file being tested")
    user_goal: str = Field(description="Goal for the simulated user")
    user_persona: Optional[str] = Field(
        default=None,
        description="Persona description for the simulated user"
    )
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
        description="When to stop the conversation"
    )
    template_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables to apply to the prompt"
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider for simulation (uses prompt's config if not provided)"
    )
    model: Optional[str] = Field(
        default=None,
        description="LLM model for simulation (uses prompt's config if not provided)"
    )


# ==============================================================================
# API Endpoints
# ==============================================================================

@router.post(
    "/simulate",
    response_model=StandardResponse[SimulateConversationResponse],
    status_code=status.HTTP_200_OK,
    summary="Simulate a conversation based on user goal",
    description="Simulate a multi-turn conversation by having AI play the user role with a specific goal.",
    responses={
        400: {"description": "Bad request - invalid parameters"},
        503: {"description": "Service unavailable - simulation failed"},
    },
)
async def simulate_conversation(
    request: Request,
    body: SimulateConversationApiRequest,
    user_id: CurrentUserDep,
    conversation_simulator_service: ConversationSimulatorServiceDep,
) -> StandardResponse[SimulateConversationResponse]:
    """
    Simulate a conversation based on user goal.

    This endpoint simulates a multi-turn conversation by:
    1. Using AI to simulate a user with a specific goal
    2. Getting responses from the actual chatbot being tested
    3. Continuing until the goal is achieved or max turns reached
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        f"Simulate conversation request for prompt {body.prompt_reference} with goal: {body.user_goal}",
        extra={"request_id": request_id, "user_id": user_id}
    )

    # Build the service request
    service_request = SimulateConversationRequest(
        prompt_reference=body.prompt_reference,
        user_goal=body.user_goal,
        user_persona=body.user_persona,
        min_turns=body.min_turns,
        max_turns=body.max_turns,
        stopping_criteria=body.stopping_criteria,
        template_variables=body.template_variables,
        provider=body.provider,
        model=body.model,
    )

    result = await conversation_simulator_service.simulate_conversation(
        request=service_request,
        user_id=user_id,
        repo_name=body.repo_name,
    )

    return StandardResponse(data=result)
