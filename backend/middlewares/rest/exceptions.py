"""
Custom exception classes for standardized error handling.
"""
from typing import Optional, Dict, Any, List
from fastapi import status


class AppException(Exception):
    """
    Base application exception class.
    All custom exceptions should inherit from this.
    """
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        message: str = "An error occurred",
        detail: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail or message
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for response."""
        return {
            "code": self.error_code,
            "message": self.message,
            "context": self.context
        }


class ValidationException(AppException):
    """Raised when request validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            context=context
        )
        self.errors = errors or []


class AuthenticationException(AppException):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication required",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_REQUIRED",
            message=message,
            context=context
        )


class AuthorizationException(AppException):
    """Raised when authorization fails."""
    
    def __init__(
        self,
        message: str = "Access denied",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="ACCESS_DENIED",
            message=message,
            context=context
        )


class NotFoundException(AppException):
    """Raised when a resource is not found."""
    
    def __init__(
        self,
        resource: str = "Resource",
        identifier: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
            context=context
        )


class ConflictException(AppException):
    """Raised when there's a conflict with the current state."""
    
    def __init__(
        self,
        message: str = "Operation conflicts with current state",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            context=context
        )


class BadRequestException(AppException):
    """Raised for bad requests."""
    
    def __init__(
        self,
        message: str = "Bad request",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            message=message,
            context=context
        )


class ServiceUnavailableException(AppException):
    """Raised when a service is temporarily unavailable."""
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            message=message,
            context=context
        )


class RateLimitException(AppException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        context = context or {}
        if retry_after:
            context["retry_after"] = retry_after
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message=message,
            context=context
        )