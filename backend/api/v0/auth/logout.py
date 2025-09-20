"""
Logout endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status
from sqlmodel import Session

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    AuthenticationException
)
from models.database import get_session
from .verify import get_bearer_token
from api.deps import get_auth_service
from services.auth.auth_service import AuthService
from services.auth.models import LogoutRequest, AuthError, SessionNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/logout",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user and invalidate session"
)
async def logout(
    request: Request,
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> StandardResponse[dict]:
    """
    Logout user and invalidate session.
    
    Returns:
        StandardResponse[dict]: Standardized response confirming logout
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Create logout request using auth service models
        logout_request = LogoutRequest(session_token=token)
        logout_response = await auth_service.logout(logout_request, db)
        
        return success_response(
            data={
                "status": logout_response.status,
                "message": logout_response.message
            },
            message="User logged out successfully",
            meta={"request_id": request_id}
        )
        
    except SessionNotFoundError:
        raise AuthenticationException(message="Session not found")
    except AuthError as e:
        logger.error(
            f"Auth error during logout: {e}",
            extra={"request_id": request_id}
        )
        raise AppException(message=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error during logout: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(message="Failed to logout")