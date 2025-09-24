"""
Pydantic database.models for REST middleware utilities.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class RequestMetadata(BaseModel):
    """Model for request metadata."""
    request_id: str = Field(..., description="Unique request identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation ID from headers")
    user_agent: Optional[str] = Field(None, description="User agent from headers")
    client_ip: Optional[str] = Field(None, description="Client IP address")


class PaginationMetadata(BaseModel):
    """Model for pagination metadata."""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class ErrorDetails(BaseModel):
    """Model for error details in exception responses."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional error context")
    detail: Optional[str] = Field(None, description="Detailed error message")