"""
Common dependencies for FastAPI routes.
"""
import uuid
from typing import Optional
from fastapi import Request, Header
from middlewares.rest.models import RequestMetadata


def get_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{uuid.uuid4().hex[:12]}"


def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID")
) -> Optional[str]:
    """Extract correlation ID from headers."""
    return x_correlation_id


def get_request_metadata(request: Request) -> RequestMetadata:
    """Extract metadata from the request."""
    return RequestMetadata(
        request_id=get_request_id(),
        correlation_id=request.headers.get("X-Correlation-ID"),
        user_agent=request.headers.get("User-Agent"),
        client_ip=request.client.host if request.client else None,
    )