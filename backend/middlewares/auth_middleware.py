"""
Authentication middleware for FastAPI.
Validates bearer tokens for all requests except whitelisted public endpoints.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from typing import Set

from utils.auth_utils import get_bearer_token, verify_session
from models.database import get_session
from services.session_service import SessionService
from services.config.factory import ConfigStrategyFactory

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates authentication for all requests except public endpoints.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
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

        # Skip auth if hosting type is individual
        try:
            config_strategy = ConfigStrategyFactory.get_strategy()
            hosting_config = config_strategy.get_hosting_config()
            hosting_type = hosting_config.type.value
            if hosting_type == "individual":
                logger.debug(f"Skipping auth for individual hosting type")
                return await call_next(request)
        except Exception as e:
            logger.warning(f"Failed to get hosting type, continuing with auth check: {e}")

        # First, let the request proceed to check if the route exists
        # This is done by temporarily proceeding without auth to see if we get a 404
        try:
            # Check if we have authorization header
            auth_header = request.headers.get("Authorization")
            
            # If no auth header, proceed to let FastAPI handle the request
            # This allows 404 responses for non-existent endpoints
            if not auth_header:
                response = await call_next(request)
                # If the response is 404, return it as-is (route doesn't exist)
                if response.status_code == 404:
                    return response
                # Otherwise, return 401 for missing auth on existing routes
                return self._unauthorized_response("Authorization header required")

            if not auth_header.startswith("Bearer "):
                response = await call_next(request)
                # If the response is 404, return it as-is (route doesn't exist)
                if response.status_code == 404:
                    return response
                # Otherwise, return 401 for invalid auth format on existing routes
                return self._unauthorized_response("Invalid authorization header format")

            token = auth_header.replace("Bearer ", "")

            # Verify session using the existing auth utility
            db_gen = get_session()
            db = next(db_gen)
            try:
                if not SessionService.is_session_valid(db, token):
                    response = await call_next(request)
                    # If the response is 404, return it as-is (route doesn't exist)
                    if response.status_code == 404:
                        return response
                    # Otherwise, return 401 for invalid session on existing routes
                    return self._unauthorized_response("Invalid or expired session token")
                
                user_session = SessionService.get_session_by_id(db, token)
                if not user_session:
                    response = await call_next(request)
                    # If the response is 404, return it as-is (route doesn't exist)
                    if response.status_code == 404:
                        return response
                    # Otherwise, return 401 for session not found on existing routes
                    return self._unauthorized_response("Session not found")

                # Add user info to request state for use in endpoints
                request.state.username = user_session.username
                request.state.session_token = token
            finally:
                db.close()

            logger.debug(f"Authentication successful for user: {user_session.username}")
            return await call_next(request)

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            # On error, still check if route exists before returning auth error
            try:
                response = await call_next(request)
                if response.status_code == 404:
                    return response
            except:
                pass
            return self._unauthorized_response("Authentication failed")

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if the endpoint is in the public endpoints list."""
        # Direct match
        if path in self.public_endpoints:
            return True
        
        # Check for path patterns (for docs and static files)
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            return True
            
        return False

    def _unauthorized_response(self, detail: str) -> JSONResponse:
        """Return a standardized unauthorized response."""
        return JSONResponse(
            status_code=401,
            content={"detail": detail}
        )