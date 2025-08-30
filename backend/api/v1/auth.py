"""
Authentication routes for PromptRepo API.
Handles GitHub OAuth flow and session management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional, Annotated
from backend.models.user_sessions import User_Sessions
from backend.settings.base_settings import settings
import uuid
import secrets
from datetime import datetime, timedelta
from datetime import UTC
import logging

# Import services
from backend.services import create_github_service
from backend.services.github_service import GitHubService

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class GitHubCallbackRequest(BaseModel):
    code: str
    state: str

class AuthUrlResponse(BaseModel):
    authUrl: str

class User(BaseModel):
    id: str
    username: str
    name: str
    email: str
    avatar_url: str

class LoginResponse(BaseModel):
    user: User
    sessionToken: str
    expiresAt: str

class RefreshResponse(BaseModel):
    sessionToken: str
    expiresAt: str

class StatusResponse(BaseModel):
    status: str
    message: str

# In-memory state storage (replace with database in production)
oauth_states: dict[str, datetime] = {}
active_sessions: dict[str, dict] = {}

def cleanup_expired_states():
    """Remove expired OAuth states"""
    now = datetime.utcnow()
    expired_states = [state for state, created_at in oauth_states.items()
                     if now - created_at > timedelta(minutes=10)]
    for state in expired_states:
        oauth_states.pop(state, None)

def cleanup_expired_sessions():
    """Remove expired sessions"""
    now = datetime.now(UTC)
    expired_sessions = [token for token, data in active_sessions.items()
                       if datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00')) < now]
    for token in expired_sessions:
        active_sessions.pop(token, None)

# Dependency to extract Bearer token
async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    return authorization.replace("Bearer ", "")

@router.get("/login/github", response_model=AuthUrlResponse)
async def initiate_github_login():
    """
    Start GitHub OAuth flow.
    Returns the GitHub OAuth authorization URL.
    """
    cleanup_expired_states()

    try:
        # Create GitHub service
        github_service = create_github_service()

        # Generate authorization URL with required scopes
        scopes = ["repo", "user:email", "read:user"]
        auth_url, state = github_service.generate_auth_url(scopes=scopes)

        # Store state for CSRF verification
        oauth_states[state] = datetime.now(UTC)

        logger.info(f"Generated GitHub OAuth URL for state: {state}")

        return AuthUrlResponse(authUrl=auth_url)

    except ValueError as e:
        logger.error(f"GitHub service configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not properly configured"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authentication URL"
        )


@router.get("/callback/github", response_model=LoginResponse)
async def github_oauth_callback(code: str, state: str):
    """
    Handle GitHub OAuth callback.
    Exchange the authorization code for an access token and create user session.
    """
    cleanup_expired_states()
    cleanup_expired_sessions()

    # Verify state parameter for CSRF protection
    if state not in oauth_states:
        logger.warning(f"Invalid or expired state parameter: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter"
        )

    # Remove used state
    oauth_states.pop(state)

    try:
        # Create GitHub service
        github_service = create_github_service()

        async with github_service:
            # Exchange code for access token
            token_response = await github_service.exchange_code_for_token(
                code=code,
                state=state
            )

            # Get user information
            github_user = await github_service.get_user_info(token_response.access_token)

            # Get user's primary email
            primary_email = await github_service.get_primary_email(token_response.access_token)

            # Create user object
            user = User(
                id=str(github_user.id),
                username=github_user.login,
                name=github_user.name or github_user.login,
                email=primary_email or "",
                avatar_url=github_user.avatar_url
            )

            session_id = User_Sessions.generate_session_key()
            user_session = User_Sessions(
                username=github_user.login,
                session_id=session_id,
                oauth_token=token_response.access_token
            )
            expires_at = datetime.now(UTC) + timedelta(minutes=settings.session_key_expiry_minutes)

            logger.info(f"Successfully authenticated user: {github_user.login}")

            return LoginResponse(
                user=user,
                sessionToken=session_id,
                expiresAt=expires_at.isoformat() + "Z"
            )

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed due to server error"
        )

@router.get("/verify", response_model=User)
async def verify_session(token: str = Depends(get_bearer_token)):
    """
    Verify current session and return user information.
    """
    cleanup_expired_sessions()

    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    session_data = active_sessions[token]

    # Check if session has expired
    expires_at = datetime.fromisoformat(session_data['expires_at'].replace('Z', '+00:00'))
    if datetime.now(UTC) > expires_at:
        active_sessions.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired"
        )

    # Optionally validate the GitHub token is still valid
    try:
        github_service = create_github_service()
        async with github_service:
            if not await github_service.validate_token(session_data['github_token']):
                active_sessions.pop(token, None)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="GitHub token has been revoked"
                )
    except Exception as e:
        logger.warning(f"Could not validate GitHub token: {e}")
        # Continue without validation if GitHub is unreachable

    return User(**session_data['user'])

@router.post("/logout", response_model=StatusResponse)
async def logout(token: str = Depends(get_bearer_token)):
    """
    Logout user and invalidate session.
    """
    if token not in active_sessions:
        # Already logged out or invalid token
        return StatusResponse(
            status="success",
            message="Successfully logged out"
        )

    session_data = active_sessions.pop(token, None)

    # Optionally revoke the GitHub token
    if session_data:
        try:
            github_service = create_github_service()
            async with github_service:
                await github_service.revoke_token(session_data['github_token'])
        except Exception as e:
            logger.warning(f"Could not revoke GitHub token: {e}")
            # Continue with logout even if revocation fails

    logger.info("User successfully logged out")

    return StatusResponse(
        status="success",
        message="Successfully logged out"
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_session(token: str = Depends(get_bearer_token)):
    """
    Refresh session token to extend expiry.
    """
    cleanup_expired_sessions()

    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    session_data = active_sessions[token]

    # Check if session has expired
    expires_at = datetime.fromisoformat(session_data['expires_at'].replace('Z', '+00:00'))
    if datetime.now(UTC) > expires_at:
        active_sessions.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired"
        )

    # Generate new session token and extend expiry
    new_session_token = secrets.token_urlsafe(32)
    new_expires_at = datetime.now(UTC) + timedelta(hours=24)

    # Move session data to new token
    session_data['expires_at'] = new_expires_at.isoformat() + "Z"
    active_sessions[new_session_token] = session_data
    active_sessions.pop(token, None)

    logger.info("Session successfully refreshed")
    return RefreshResponse(
        sessionToken=new_session_token,
        expiresAt=new_expires_at.isoformat() + "Z"
    )

# Health check for auth routes
@router.get("/health")
async def auth_health_check():
    """Health check specifically for auth routes."""
    cleanup_expired_states()
    cleanup_expired_sessions()

    return {
        "status": "healthy",
        "service": "authentication",
        "active_sessions": len(active_sessions),
        "pending_oauth_states": len(oauth_states),
        "endpoints": [
            "GET /login/github",
            "POST /callback/github",
            "GET /verify",
            "POST /logout",
            "POST /refresh"
        ]
    }