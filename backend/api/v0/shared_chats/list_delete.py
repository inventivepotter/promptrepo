"""
List and delete shared chats endpoints.
"""
import logging
from typing import List
from fastapi import APIRouter, Request, status, Query

from schemas.shared_chat import SharedChatListItem
from api.deps import SharedChatServiceDep, CurrentUserDep
from middlewares.rest import StandardResponse, success_response, AppException, NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=StandardResponse[List[SharedChatListItem]],
    status_code=status.HTTP_200_OK,
    summary="List user's shared chats",
    description="List all shared chats created by the current user",
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
                        "detail": "Failed to list shared chats"
                    }
                }
            }
        }
    },
)
async def list_shared_chats(
    request: Request,
    service: SharedChatServiceDep,
    current_user: CurrentUserDep,
    limit: int = Query(default=50, ge=1, le=100, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination")
) -> StandardResponse[List[SharedChatListItem]]:
    """
    List all shared chats created by the current user.

    Args:
        request: FastAPI request
        service: SharedChatService dependency
        current_user: Current authenticated user ID
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        StandardResponse containing list of shared chats
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Listing shared chats",
            extra={
                "request_id": request_id,
                "user_id": current_user,
                "limit": limit,
                "offset": offset
            }
        )

        result = service.list_user_shared_chats(
            user_id=current_user,
            limit=limit,
            offset=offset
        )

        logger.info(
            "Shared chats listed successfully",
            extra={
                "request_id": request_id,
                "user_id": current_user,
                "count": len(result)
            }
        )

        return success_response(
            data=result,
            message="Shared chats retrieved successfully",
            meta={"request_id": request_id, "count": len(result)}
        )

    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to list shared chats: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": current_user}
        )
        raise AppException(
            message="Failed to list shared chats",
            detail=str(e)
        )


@router.delete(
    "/{share_id}",
    response_model=StandardResponse[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete shared chat",
    description="Delete a shared chat (only owner can delete)",
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
        404: {
            "description": "Shared chat not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Shared chat not found or you don't have permission"
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
                        "detail": "Failed to delete shared chat"
                    }
                }
            }
        }
    },
)
async def delete_shared_chat(
    request: Request,
    share_id: str,
    service: SharedChatServiceDep,
    current_user: CurrentUserDep
) -> StandardResponse[bool]:
    """
    Delete a shared chat.

    Only the owner can delete their shared chat.

    Args:
        request: FastAPI request
        share_id: The share identifier
        service: SharedChatService dependency
        current_user: Current authenticated user ID

    Returns:
        StandardResponse containing success boolean
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Deleting shared chat",
            extra={
                "request_id": request_id,
                "user_id": current_user,
                "share_id": share_id
            }
        )

        result = service.delete_shared_chat(share_id, user_id=current_user)

        logger.info(
            "Shared chat deleted successfully",
            extra={
                "request_id": request_id,
                "user_id": current_user,
                "share_id": share_id
            }
        )

        return success_response(
            data=result,
            message="Shared chat deleted successfully",
            meta={"request_id": request_id}
        )

    except NotFoundException:
        raise
    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete shared chat: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": current_user}
        )
        raise AppException(
            message="Failed to delete shared chat",
            detail=str(e)
        )
