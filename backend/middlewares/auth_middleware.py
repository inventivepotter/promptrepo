"""
Authentication middleware for FastAPI.
Validates bearer tokens for all requests except whitelisted public endpoints.
"""
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from typing import Set, Optional

from api.deps import get_session_service, get_db
from services.config.config_service import ConfigService
from services.config.models import HostingType
from middlewares.rest.exceptions import AuthenticationException

logger = logging.getLogger(__name__)

# User ID to use when hosting type is INDIVIDUAL
INDIVIDUAL_USER_ID = "individual-user"


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates authentication for all requests except public endpoints.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

        hosting_type = ConfigService().get_hosting_config().type
        logger.info(f"\n\n\n\nHosting type: {hosting_type}")
        # Define public endpoints that don't require authentication
        self.public_endpoints: Set[str] = {
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            # Auth endpoints
            "/api/v0/auth/login/github",
            "/api/v0/auth/callback/github",
            "/api/v0/auth/login",
            "/api/v0/auth/callback",
            "/api/v0/auth/verify",
            "/api/v0/auth/logout",
            "/api/v0/auth/refresh",
            # Public provider info (available providers without requiring auth)
            "/api/v0/llm/providers/available",
            # Public config endpoints
            "/api/v0/config/hosting-type",
        }

    async def dispatch(self, request: Request, call_next):
        """Process the request and validate authentication if needed."""
        
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            logger.debug(f"Skipping auth for public endpoint: {request.url.path}")
            return await call_next(request)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Check hosting type and skip auth if individual
        try:
            hosting_type = ConfigService().get_hosting_config().type
            logger.info(f"\n\n\n\nHosting type: {hosting_type}")
            if hosting_type == HostingType.INDIVIDUAL:
                logger.debug(f"Skipping auth for individual hosting type, setting user_id to '{INDIVIDUAL_USER_ID}'")
                request.state.user_id = INDIVIDUAL_USER_ID
                return await call_next(request)
        except Exception as e:
            logger.warning(f"Failed to get hosting type, continuing with auth check: {e}")
            hosting_type = None

        # Extract and validate Bearer token
        token = self._extract_bearer_token(request)
        if not token:
            raise AuthenticationException("Authorization header required")

        try:
            # Manually get DB session for use in middleware
            db = next(get_db())
            # Get SessionService instance from dependency
            session_service = get_session_service(db)
            
            if not session_service.is_session_valid(token):
                raise AuthenticationException("Invalid or expired session token")
            
            user_session = session_service.get_session_by_id(token)
            if not user_session:
                raise AuthenticationException("Session not found")

            # Add user info to request state for use in endpoints
            request.state.user_id = user_session.user_id
            request.state.session_token = token

            logger.debug(f"Authentication successful for user: {user_session.user.username}")
            return await call_next(request)

        except AuthenticationException:
            # Re-raise authentication exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            raise AuthenticationException("Authentication failed")

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if the endpoint is in the public endpoints list."""
        # Direct match
        if path in self.public_endpoints:
            return True
        
        # Check for path patterns (for docs and static files)
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            return True
            
        return False

    def _extract_bearer_token(self, request: Request) -> Optional[str]:
        """
        Safely extract Bearer token from Authorization header.
        Returns None if no valid Bearer token found.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        # Split the header to validate format
        parts = auth_header.split()
        if len(parts) != 2:
            return None
            
        scheme, token = parts
        if scheme.lower() != "bearer":
            return None
            
        # Additional validation: ensure token is not empty
        if not token or token.isspace():
            return None
            
        return token
