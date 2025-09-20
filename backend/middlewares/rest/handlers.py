"""
Global exception handlers for FastAPI application.
"""
import logging
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .responses import error_response, ErrorDetail
from .exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions.
    """
    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    
    errors = []
    
    # Check if it's a ValidationException with errors
    from .exceptions import ValidationException
    if isinstance(exc, ValidationException) and exc.errors:
        for err in exc.errors:
            errors.append(
                ErrorDetail(
                    code=err.get("code", exc.error_code),
                    message=err.get("message", ""),
                    field=err.get("field"),
                    context=err.get("context")
                )
            )
    else:
        # Convert the exception itself to an ErrorDetail
        errors.append(
            ErrorDetail(
                code=exc.error_code,
                message=exc.message,
                field=None,
                context=exc.context
            )
        )
    
    response = error_response(
        error_type=f"/errors/{exc.error_code.lower().replace('_', '-')}",
        title=exc.message,
        detail=exc.detail,
        errors=errors,
        instance=request.url.path,
        meta={
            "request_id": request_id,
            "correlation_id": correlation_id
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(exclude_none=True)
    )


async def http_exception_handler(
    request: Request, 
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """
    Handle FastAPI/Starlette HTTP exceptions.
    """
    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    
    # Map status codes to error types
    error_type_map = {
        400: "bad-request",
        401: "unauthorized",
        403: "forbidden",
        404: "not-found",
        405: "method-not-allowed",
        409: "conflict",
        422: "validation-failed",
        429: "rate-limit-exceeded",
        500: "internal-server-error",
        502: "bad-gateway",
        503: "service-unavailable",
        504: "gateway-timeout",
    }
    
    error_type = error_type_map.get(exc.status_code, "error")
    
    response = error_response(
        error_type=f"/errors/{error_type}",
        title=getattr(exc, "detail", "Error"),
        detail=getattr(exc, "detail", None),
        instance=request.url.path,
        meta={
            "request_id": request_id,
            "correlation_id": correlation_id
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(exclude_none=True)
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.
    """
    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append(
            ErrorDetail(
                code="VALIDATION_ERROR",
                message=error.get("msg", "Validation failed"),
                field=field_path,
                context={
                    "type": error.get("type"),
                    "input": error.get("input")
                }
            )
        )
    
    response = error_response(
        error_type="/errors/validation-failed",
        title="Validation Error",
        detail="The request contains invalid data",
        errors=errors,
        instance=request.url.path,
        meta={
            "request_id": request_id,
            "correlation_id": correlation_id
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(exclude_none=True)
    )


async def pydantic_exception_handler(
    request: Request, 
    exc: ValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    """
    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append(
            ErrorDetail(
                code="VALIDATION_ERROR",
                message=error.get("msg", "Validation failed"),
                field=field_path,
                context={"type": error.get("type")}
            )
        )
    
    response = error_response(
        error_type="/errors/validation-failed",
        title="Data Validation Error",
        detail="The provided data failed validation",
        errors=errors,
        instance=request.url.path,
        meta={
            "request_id": request_id,
            "correlation_id": correlation_id
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(exclude_none=True)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    """
    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    
    # Log the full exception
    logger.error(
        f"Unhandled exception in request {request_id}",
        exc_info=exc,
        extra={
            "request_id": request_id,
            "correlation_id": correlation_id,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    response = error_response(
        error_type="/errors/internal-server-error",
        title="Internal Server Error",
        detail="An unexpected error occurred while processing your request",
        instance=request.url.path,
        meta={
            "request_id": request_id,
            "correlation_id": correlation_id
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(exclude_none=True)
    )