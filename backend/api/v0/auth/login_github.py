"""
GitHub login initiation endpoint with standardized responses.
"""
import logging
import secrets
from datetime import datetime, UTC
from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from services import create_github_service

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory OAuth state storage (you might want to move this to database too)
oauth_states: dict[str, datetime] = {}

def cleanup_expired_states():
    """Remove expired OAuth states"""
    from datetime import timedelta
    now = datetime.now(UTC)
    expired_states = [state for state, created_at in oauth_states.items()
                     if now - created_at > timedelta(minutes=10)]
    for state in expired_states:
        oauth_states.pop(state, None)


class AuthUrlResponse(BaseModel):
    authUrl: str


@router.get(
    "/login/github",
    response_model=StandardResponse[AuthUrlResponse],
    status_code=status.HTTP_200_OK,
    responses={
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/service-unavailable",
                        "title": "Service unavailable",
                        "detail": "GitHub OAuth is not properly configured"
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
                        "detail": "Failed to generate authentication URL"
                    }
                }
            }
        }
    },
    summary="Initiate GitHub login",
    description="Start GitHub OAuth flow and get authorization URL"
)
async def initiate_github_login(request: Request) -> StandardResponse[AuthUrlResponse]:
    """
    Start GitHub OAuth flow.
    Returns the GitHub OAuth authorization URL.
    
    Returns:
        StandardResponse[AuthUrlResponse]: Standardized response containing the auth URL
    
    Raises:
        AppException: When OAuth URL generation fails
    """
    request_id = getattr(request.state, "request_id", None)
    cleanup_expired_states()

    try:
        # Create GitHub service
        github_service = create_github_service()

        # Generate authorization URL with required scopes
        scopes = ["repo", "user:email", "read:user"]
        auth_url, state = github_service.generate_auth_url(scopes=scopes)

        # Store state for CSRF verification
        oauth_states[state] = datetime.now(UTC)

        logger.info(
            f"Generated GitHub OAuth URL",
            extra={
                "request_id": request_id,
                "state": state
            }
        )

        return success_response(
            data=AuthUrlResponse(authUrl=auth_url),
            message="GitHub authorization URL generated successfully",
            meta={"request_id": request_id}
        )

    except ValueError as e:
        logger.error(
            f"GitHub service configuration error: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="GitHub OAuth is not properly configured",
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Unexpected error generating auth URL: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to generate authentication URL",
            detail=str(e)
        )