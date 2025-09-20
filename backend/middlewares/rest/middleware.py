"""
Middleware for request/response processing and standardization.
"""
import time
import json
import logging
from typing import Callable, Any
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .responses import create_response, error_response, ResponseStatus
from .exceptions import AppException

logger = logging.getLogger(__name__)


class ResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware to standardize all responses and add metadata.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID", f"req_{uuid4().hex[:12]}")
        correlation_id = request.headers.get("X-Correlation-ID")
        
        # Store in request state for access in endpoints
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        # Track request time
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add standard headers
            response.headers["X-Request-ID"] = request_id
            if correlation_id:
                response.headers["X-Correlation-ID"] = correlation_id
            
            # Add timing header
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request {request_id} failed after {process_time:.3f}s",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                }
            )
            
            # Return standardized error response
            error_resp = error_response(
                error_type="/errors/internal-server-error",
                title="Internal Server Error",
                detail="An unexpected error occurred",
                meta={
                    "request_id": request_id,
                    "correlation_id": correlation_id
                }
            )
            
            return JSONResponse(
                status_code=500,
                content=error_resp.model_dump(exclude_none=True),
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": str(process_time)
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request/response logging.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle response compression.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" in accept_encoding.lower() and response.status_code == 200:
            # Note: In production, use a proper compression library
            # This is a placeholder for the compression logic
            response.headers["Content-Encoding"] = "gzip"
        
        return response