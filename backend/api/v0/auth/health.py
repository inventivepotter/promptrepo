"""
Auth service health check endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status
from sqlmodel import Session, select, func

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from models.database import get_session
from api.deps import get_auth_service
from services.auth.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Authentication health check",
    description="Health check specifically for auth routes"
)
async def auth_health_check(
    request: Request,
    db: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> StandardResponse[dict]:
    """Health check specifically for auth routes."""
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Clean up expired sessions and OAuth states using auth service
        expired_count = auth_service.cleanup_expired_sessions(db)

        statement = select(func.count())
        active_sessions_count = db.exec(statement).one()

        health_data = {
            "status": "healthy",
            "service": "authentication",
            "active_sessions": active_sessions_count,
            "expired_sessions_cleaned": expired_count,
            "pending_oauth_states": 0,  # OAuth states are now managed internally by the OAuth service
            "endpoints": [
                "GET /login/github",
                "GET /callback/github",
                "GET /verify",
                "POST /logout",
                "POST /refresh"
            ]
        }

        return success_response(
            data=health_data,
            message="Authentication service is healthy",
            meta={"request_id": request_id}
        )
        
    except Exception as e:
        logger.error(
            f"Health check failed: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Health check failed",
            detail=str(e)
        )