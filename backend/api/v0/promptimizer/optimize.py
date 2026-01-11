"""
Prompt optimization API endpoint.

This endpoint provides AI-powered prompt enhancement using provider-specific
best practices and optional OWASP security guardrails.
"""
import logging
from fastapi import APIRouter, Request, status

from middlewares.rest import StandardResponse, success_response
from middlewares.rest.exceptions import BadRequestException, AppException
from services.promptimizer.models import PromptOptimizerRequest, PromptOptimizerResponse
from services.promptimizer.promptimizer_service import PromptOptimizerService
from api.deps import ConfigServiceDep, CurrentUserDep

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/optimize",
    response_model=StandardResponse[PromptOptimizerResponse],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Bad request - invalid input"},
        401: {"description": "Unauthorized - authentication required"},
        500: {"description": "Internal server error"}
    },
    summary="Optimize prompt",
    description="""
    Optimize a system prompt based on user's idea and provider-specific best practices.

    This endpoint uses an AI agent to enhance prompts by:
    - Applying provider-specific best practices (OpenAI, Anthropic, Google Gemini)
    - Adding OWASP 2025 prompt injection guardrails (when expects_user_message is true)
    - Supporting multi-turn refinement through conversation_history

    The optimized prompt is returned without any wrapping or meta-commentary.
    """
)
async def optimize_prompt(
    request_body: PromptOptimizerRequest,
    request: Request,
    config_service: ConfigServiceDep,
    user_id: CurrentUserDep
) -> StandardResponse[PromptOptimizerResponse]:
    """
    Optimize a prompt using AI assistance.

    Args:
        request_body: PromptOptimizerRequest containing idea, provider, model, etc.
        request: FastAPI request object
        config_service: Config service for LLM configuration lookup
        user_id: Authenticated user ID

    Returns:
        StandardResponse containing the optimized prompt

    Raises:
        BadRequestException: If request validation fails
        AppException: If optimization fails
    """
    request_id = getattr(request.state, "request_id", None)

    try:
        # Validate required fields
        if not request_body.idea or not request_body.idea.strip():
            raise BadRequestException(
                message="Idea is required",
                context={"request_id": request_id}
            )

        logger.info(
            "Prompt optimization request received",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "provider": request_body.provider,
                "model": request_body.model,
                "expects_user_message": request_body.expects_user_message,
                "has_conversation_history": bool(request_body.conversation_history)
            }
        )

        # Create service and execute optimization
        service = PromptOptimizerService(config_service=config_service)
        response = await service.optimize_prompt(request_body, user_id)

        logger.info(
            "Prompt optimization completed successfully",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "output_length": len(response.optimized_prompt)
            }
        )

        return success_response(
            data=response,
            message="Prompt optimized successfully",
            meta={"request_id": request_id}
        )

    except (BadRequestException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Prompt optimization failed: {e}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Prompt optimization failed",
            detail=str(e)
        )
