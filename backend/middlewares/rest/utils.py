"""
Utility functions for API operations.
"""
from typing import Optional, Dict, Any, List, TypeVar
from datetime import datetime, timezone
from fastapi import Query, Depends

T = TypeVar("T")


class PaginationParams:
    """
    Common pagination parameters for list endpoints.
    """
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.limit = page_size


class FilterParams:
    """
    Common filter parameters for list endpoints.
    """
    
    def __init__(
        self,
        search: Optional[str] = Query(None, description="Search term"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
        created_after: Optional[datetime] = Query(None, description="Filter by creation date"),
        created_before: Optional[datetime] = Query(None, description="Filter by creation date"),
    ):
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.created_after = created_after
        self.created_before = created_before


def normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normalize datetime to UTC timezone.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if no timezone
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def sanitize_dict(data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Remove sensitive information from dictionary.
    """
    if sensitive_keys is None:
        sensitive_keys = ["password", "api_key", "secret", "token", "apiKey"]
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, sensitive_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def calculate_pagination_metadata(
    total_items: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Calculate pagination metadata.
    """
    total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


# Dependency for getting pagination params
def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """
    Get pagination parameters from query params.
    """
    return PaginationParams(page=page, page_size=page_size)


# Dependency for getting filter params
def get_filters(
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
) -> FilterParams:
    """
    Get filter parameters from query params.
    """
    return FilterParams(
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )