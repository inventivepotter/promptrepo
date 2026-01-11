"""
Create shared chat endpoint.
"""
import logging
from fastapi import APIRouter, Request, status

from schemas.shared_chat import CreateSharedChatRequest, CreateSharedChatResponse
from api.deps import SharedChatServiceDep, CurrentUserDep
from middlewares.rest import StandardResponse, success_response, AppException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=StandardResponse[CreateSharedChatResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create shared chat",
    description="Create a shareable link for a chat session",
    responses={
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/authentication-error",
                        "title": "Authentication Required",
                        "detail": "Please login to access this resource"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to create shared chat"
                    }
                }
            }
        }
    },
)
async def create_shared_chat(
    request: Request,
    body: CreateSharedChatRequest,
    service: SharedChatServiceDep,
    current_user: CurrentUserDep
) -> StandardResponse[CreateSharedChatResponse]:
    """
    Create a new shared chat link.

    Args:
        request: FastAPI request
        body: CreateSharedChatRequest with chat data
        service: SharedChatService dependency
        current_user: Current authenticated user ID

    Returns:
        StandardResponse containing share ID and URL
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Creating shared chat",
            extra={
                "request_id": request_id,
                "user_id": current_user,
                "message_count": len(body.messages)
            }
        )

        result = service.create_shared_chat(body, user_id=current_user)

        logger.info(
            "Shared chat created successfully",
            extra={
                "request_id": request_id,
                "user_id": current_user,
                "share_id": result.share_id
            }
        )

        return success_response(
            data=result,
            message="Shared chat created successfully",
            meta={"request_id": request_id}
        )

    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create shared chat: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": current_user}
        )
        raise AppException(
            message="Failed to create shared chat",
            detail=str(e)
        )
