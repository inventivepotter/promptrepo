"""
Core utilities and configurations for the FastAPI application.
"""
from .responses import (
    StandardResponse,
    ErrorResponse,
    ValidationErrorResponse,
    PaginatedResponse,
    create_response,
    success_response,
    error_response,
    paginated_response,
)
from .exceptions import (
    AppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    BadRequestException,
)
from .dependencies import (
    get_request_id,
    get_correlation_id,
)

__all__ = [
    # Responses
    "StandardResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "PaginatedResponse",
    "create_response",
    "success_response",
    "error_response",
    "paginated_response",
    
    # Exceptions
    "AppException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "ConflictException",
    "BadRequestException",
    
    # Dependencies
    "get_request_id",
    "get_correlation_id",
]