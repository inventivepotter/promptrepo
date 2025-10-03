"""
Application setup and configuration module.
Handles all FastAPI configuration, middleware, and exception handlers.
"""
import os
import logging
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError

from .middleware import ResponseMiddleware, LoggingMiddleware
from .handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    pydantic_exception_handler,
    general_exception_handler,
    oauth_token_invalid_handler,
)
from .exceptions import AppException, OAuthTokenInvalidException

logger = logging.getLogger(__name__)


class FastAPISetup:
    """
    Centralized FastAPI setup and configuration.
    Follows the same pattern as AuthMiddleware for clean separation.
    """
    
    def __init__(
        self,
        title: str = "FastAPI Application",
        description: str = "API Application",
        version: str = "1.0.0",
        environment: Optional[str] = None
    ):
        self.title = title
        self.description = description
        self.version = version
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
        
    def configure_app(self, app: FastAPI) -> FastAPI:
        """
        Configure the FastAPI application with all necessary settings.
        """
        self._configure_openapi(app)
        self._register_exception_handlers(app)
        self._add_middleware(app)
        
        logger.info(
            f"FastAPI application configured: {self.title} v{self.version} "
            f"[{self.environment}]"
        )
        
        return app
    
    def _configure_openapi(self, app: FastAPI):
        """Configure OpenAPI documentation settings."""
        app.title = self.title
        app.description = self.description
        app.version = self.version
        app.docs_url = "/docs" if not self.is_production else None
        app.redoc_url = "/redoc" if not self.is_production else None
        app.openapi_url = "/openapi.json"
        
        # Add OpenAPI tags
        if not hasattr(app, 'openapi_tags') or not app.openapi_tags:
            app.openapi_tags = self._get_openapi_tags()
    
    def _get_openapi_tags(self):
        """Get OpenAPI tag definitions."""
        return [
            {
                "name": "authentication",
                "description": "Authentication and authorization operations",
            },
            {
                "name": "config",
                "description": "Configuration management operations",
            },
            {
                "name": "llm",
                "description": "LLM provider and chat operations",
            },
            {
                "name": "monitoring",
                "description": "Health checks and monitoring endpoints",
            },
            {
                "name": "info",
                "description": "API information endpoints",
            },
        ]
    
    
    def _register_exception_handlers(self, app: FastAPI):
        """Register all exception handlers."""
        # Type-ignore comments are necessary because FastAPI's type hints
        # don't properly support custom exception handler signatures
        
        # OAuth token invalid (must be registered before AppException)
        app.add_exception_handler(OAuthTokenInvalidException, oauth_token_invalid_handler)  # type: ignore
        
        # Custom application exceptions
        app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
        
        # FastAPI/Starlette exceptions
        app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
        
        # Validation exceptions
        app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
        app.add_exception_handler(ValidationError, pydantic_exception_handler)  # type: ignore
        
        # General exceptions (only in production)
        if self.is_production:
            app.add_exception_handler(Exception, general_exception_handler)  # type: ignore
        
        logger.info("Exception handlers registered")
    
    def _add_middleware(self, app: FastAPI):
        """
        Add middleware stack in correct order.
        Note: Middleware is executed in reverse order of registration.
        """
        # Response standardization (outermost - runs last on response)
        app.add_middleware(ResponseMiddleware)
        
        # Logging
        app.add_middleware(LoggingMiddleware)
        
        # Security middleware (production only)
        if self.is_production:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=self._get_allowed_hosts()
            )
        
        # Compression
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self._get_cors_origins(),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID", "X-Process-Time", "X-Correlation-ID"],
        )
        
        logger.info("Middleware stack configured")
    
    def _get_allowed_hosts(self):
        """Get allowed hosts for TrustedHost middleware."""
        # Get from environment or use defaults
        hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
        if hosts and hosts[0]:
            return hosts
        
        # Default for production
        return ["*.promptrepo.dev", "promptrepo.dev"]
    
    def _get_cors_origins(self):
        """Get CORS allowed origins."""
        # Get from environment or use defaults
        origins = os.getenv("CORS_ORIGINS", "").split(",")
        if origins and origins[0]:
            return origins
        
        # Defaults based on environment
        if self.is_production:
            return [
                "https://promptrepo.dev",
                "https://www.promptrepo.dev",
            ]
        else:
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",  # Vite default
                "http://127.0.0.1:5173",
            ]


def setup_fastapi_app(
    app: FastAPI,
    title: str = "FastAPI Application",
    description: str = "API Application",
    version: str = "1.0.0",
    environment: Optional[str] = None
) -> FastAPI:
    """
    Convenience function to setup a FastAPI application.
    
    Usage:
        from core.setup import setup_fastapi_app
        
        app = FastAPI(lifespan=lifespan)
        app = setup_fastapi_app(
            app,
            title="PromptRepo API",
            description="Backend API for PromptRepo",
            version="1.0.0"
        )
    """
    setup = FastAPISetup(
        title=title,
        description=description,
        version=version,
        environment=environment
    )
    return setup.configure_app(app)