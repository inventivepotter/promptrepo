"""
Get shared chat endpoint (public).
"""
import logging
from fastapi import APIRouter, Request, status

from schemas.shared_chat import SharedChatResponse
from api.deps import SharedChatServiceDep
from middlewares.rest import StandardResponse, success_response, AppException, NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{share_id}",
    response_model=StandardResponse[SharedChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Get shared chat",
    description="Retrieve a shared chat by its share ID (public endpoint)",
    responses={
        404: {
            "description": "Shared chat not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Shared chat not found"
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
                        "detail": "Failed to retrieve shared chat"
                    }
                }
            }
        }
    },
)
async def get_shared_chat(
    request: Request,
    share_id: str,
    service: SharedChatServiceDep
) -> StandardResponse[SharedChatResponse]:
    """
    Get a shared chat by its share ID.

    This is a public endpoint - no authentication required.

    Args:
        request: FastAPI request
        share_id: The share identifier from the URL
        service: SharedChatService dependency

    Returns:
        StandardResponse containing shared chat data
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Fetching shared chat",
            extra={"request_id": request_id, "share_id": share_id}
        )

        result = service.get_shared_chat(share_id)

        logger.info(
            "Shared chat retrieved successfully",
            extra={"request_id": request_id, "share_id": share_id}
        )

        return success_response(
            data=result,
            message="Shared chat retrieved successfully",
            meta={"request_id": request_id}
        )

    except NotFoundException:
        raise
    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve shared chat: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "share_id": share_id}
        )
        raise AppException(
            message="Failed to retrieve shared chat",
            detail=str(e)
        )
