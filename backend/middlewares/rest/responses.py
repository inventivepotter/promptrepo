"""
Standardized response database.models following OpenAPI specifications and REST best practices.
"""
from typing import TypeVar, Generic, Optional, List, Any, Dict, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, UTC
from enum import Enum


T = TypeVar("T")


class ResponseStatus(str, Enum):
    """Standard response status values."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class ResponseMeta(BaseModel):
    """Metadata included with all responses."""
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp of the response"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request identifier for tracing"
    )
    version: str = Field(
        default="1.0.0",
        description="API version"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Correlation ID for distributed tracing"
    )


class StandardResponse(BaseModel, Generic[T]):
    """
    Standard response wrapper for all successful API responses.
    Follows OpenAPI and REST best practices.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": {"id": 1, "name": "Example"},
                "message": "Operation completed successfully",
                "meta": {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "request_id": "req_123",
                    "version": "1.0.0"
                }
            }
        }
    )
    
    status: ResponseStatus = Field(
        default=ResponseStatus.SUCCESS,
        description="Response status indicator"
    )
    data: Optional[T] = Field(
        None,
        description="Response payload"
    )
    message: Optional[str] = Field(
        None,
        description="Human-readable message about the response"
    )
    meta: ResponseMeta = Field(
        default_factory=lambda: ResponseMeta(),
        description="Response metadata"
    )
    

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(
        ...,
        description="Error code for programmatic handling"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    field: Optional[str] = Field(
        None,
        description="Field that caused the error (for validation errors)"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context"
    )


class ErrorResponse(BaseModel):
    """
    Standard error response format following RFC 7807 Problem Details.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "type": "/errors/validation-failed",
                "title": "Validation Error",
                "detail": "The request body contains invalid data",
                "instance": "/api/v0/users/123",
                "errors": [
                    {
                        "code": "FIELD_REQUIRED",
                        "message": "Field is required",
                        "field": "email"
                    }
                ],
                "meta": {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "request_id": "req_123"
                }
            }
        }
    )
    
    status: ResponseStatus = Field(
        default=ResponseStatus.ERROR,
        description="Always 'error' for error responses"
    )
    type: str = Field(
        ...,
        description="URI reference that identifies the problem type"
    )
    title: str = Field(
        ...,
        description="Short, human-readable summary of the problem"
    )
    detail: Optional[str] = Field(
        None,
        description="Human-readable explanation specific to this occurrence"
    )
    instance: Optional[str] = Field(
        None,
        description="URI reference that identifies the specific occurrence"
    )
    errors: Optional[List[ErrorDetail]] = Field(
        None,
        description="List of detailed errors"
    )
    meta: ResponseMeta = Field(
        default_factory=lambda: ResponseMeta(),
        description="Response metadata"
    )


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation errors."""
    
    type: str = Field(
        default="/errors/validation-failed",
        description="Validation error type"
    )
    title: str = Field(
        default="Validation Error",
        description="Validation error title"
    )


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-based)"
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    total_items: int = Field(
        ...,
        ge=0,
        description="Total number of items across all pages"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages"
    )
    has_next: bool = Field(
        ...,
        description="Whether there is a next page"
    )
    has_previous: bool = Field(
        ...,
        description="Whether there is a previous page"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 100,
                    "total_pages": 10,
                    "has_next": True,
                    "has_previous": False
                },
                "meta": {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "request_id": "req_123"
                }
            }
        }
    )
    
    status: ResponseStatus = Field(
        default=ResponseStatus.SUCCESS,
        description="Response status"
    )
    data: List[T] = Field(
        default_factory=list,
        description="List of items in the current page"
    )
    pagination: PaginationMeta = Field(
        ...,
        description="Pagination information"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message"
    )
    meta: ResponseMeta = Field(
        default_factory=lambda: ResponseMeta(),
        description="Response metadata"
    )


# Helper functions for creating responses
def create_response(
    data: Optional[Any] = None,
    message: Optional[str] = None,
    status: ResponseStatus = ResponseStatus.SUCCESS,
    meta: Optional[Dict[str, Any]] = None
) -> StandardResponse:
    """
    Create a standard response with the provided data and metadata.
    """
    response_meta = ResponseMeta()
    if meta:
        for key, value in meta.items():
            if hasattr(response_meta, key):
                setattr(response_meta, key, value)
    
    return StandardResponse(
        status=status,
        data=data,
        message=message,
        meta=response_meta
    )


def success_response(
    data: Optional[Any] = None,
    message: str = "Operation completed successfully",
    meta: Optional[Dict[str, Any]] = None
) -> StandardResponse:
    """
    Create a success response.
    """
    # Serialize Pydantic database.models to ensure proper JSON serialization
    if data is not None and hasattr(data, 'model_dump'):
        data = data.model_dump(mode='json')
    
    return create_response(
        data=data,
        message=message,
        status=ResponseStatus.SUCCESS,
        meta=meta
    )


def error_response(
    error_type: str,
    title: str,
    detail: Optional[str] = None,
    errors: Optional[List[ErrorDetail]] = None,
    instance: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    Create an error response.
    """
    response_meta = ResponseMeta()
    if meta:
        for key, value in meta.items():
            if hasattr(response_meta, key):
                setattr(response_meta, key, value)
    
    return ErrorResponse(
        type=error_type,
        title=title,
        detail=detail,
        errors=errors,
        instance=instance,
        meta=response_meta
    )


def paginated_response(
    items: List[Any],
    page: int,
    page_size: int,
    total_items: int,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> PaginatedResponse:
    """
    Create a paginated response.
    """
    total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
    
    pagination_meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    response_meta = ResponseMeta()
    if meta:
        for key, value in meta.items():
            if hasattr(response_meta, key):
                setattr(response_meta, key, value)
    
    return PaginatedResponse(
        data=items,
        pagination=pagination_meta,
        message=message,
        meta=response_meta
    )