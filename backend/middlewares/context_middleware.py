"""
Request context middleware for FastAPI.
Sets up request context including request_id and correlation_id.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import uuid
from typing import Optional

logger = logging.getLogger(__name__)


class ContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that sets up request context for all requests.
    Authentication is now handled by FastAPI dependencies.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Process the request and set up request context."""
        
        # Generate or get request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get correlation ID from header if present, otherwise create one
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        logger.debug(
            f"Processing request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "correlation_id": correlation_id
            }
        )
        
        # Continue with the request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
