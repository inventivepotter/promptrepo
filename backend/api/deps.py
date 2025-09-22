"""
API Dependencies
Common dependencies used across API endpoints following FastAPI best practices.

This module provides centralized dependency injection for all services.
We use function-based dependencies as recommended by FastAPI documentation.
"""
from typing import Generator, Annotated
from fastapi import Depends, Header
from sqlmodel import Session
from pathlib import Path
import logging
from middlewares.rest import AuthenticationException

# Set up logger
logger = logging.getLogger(__name__)

from database.core import get_session
from services.git_provider.git_provider_service import GitProviderService
from services.auth.auth_service import AuthService
from services.auth.session_service import SessionService
from services.config.config_service import ConfigService
from services.llm.completion_service import ChatCompletionService
from services.llm.provider_service import ProviderService
from services.repo.repo_service import RepoService
from services.git.git_service import GitService
from services.repo.repo_locator_service import RepoLocatorService


# ==============================================================================
# Database Dependencies
# ==============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency with proper cleanup.
    
    This function ensures:
    1. A new session is created for each request
    2. The session is properly closed after the request
    3. Database transactions are rolled back on errors
    4. Proper cleanup happens even if exceptions occur
    
    The underlying database adapter uses a context manager (with SQLSession)
    that ensures the session is closed when the context exits.
    """
    # Get the session generator from database.core
    # This returns a generator that yields a session from a context manager
    session_generator = get_session()
    
    # Get the session from the generator
    session = next(session_generator)
    
    try:
        # Yield the session to the endpoint
        yield session
        # If we get here, the request completed successfully
        # Note: Let the service/controller explicitly commit when needed
    except Exception as e:
        # If an exception occurs during request processing, rollback
        if hasattr(session, 'rollback'):
            try:
                session.rollback()
                logger.warning(f"Rolled back database transaction due to error: {type(e).__name__}")
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
        raise  # Re-raise the original exception
    finally:
        # Complete the generator to trigger the context manager's cleanup
        # This ensures the session is properly closed
        try:
            next(session_generator)
        except StopIteration:
            # This is expected - the generator is exhausted after yielding once
            pass
        except Exception as cleanup_error:
            # Log cleanup errors but don't mask the original exception
            logger.error(f"Error during session cleanup: {cleanup_error}")


# Type alias for cleaner dependency injection
DBSession = Annotated[Session, Depends(get_db)]


# ==============================================================================
# Configuration Service
# ==============================================================================

def get_config_service(db: DBSession) -> ConfigService:
    """
    Config service dependency with database injection.
    
    The ConfigService manages different configuration strategies
    based on hosting type (individual, organization).
    Database is required for repo configs in some hosting types.
    """
    return ConfigService(db=db)


ConfigServiceDep = Annotated[ConfigService, Depends(get_config_service)]


# ==============================================================================
# Git Provider Service
# ==============================================================================

def get_git_provider_service(
    config_service: ConfigServiceDep
) -> GitProviderService:
    """
    Git Provider service dependency.
    
    Creates an GitProviderService with the configuration from ConfigService.
    Handles Git Provider operations for multiple providers (GitHub, GitLab, etc.).
    """
    return GitProviderService(config_service=config_service.config)


OAuthServiceDep = Annotated[GitProviderService, Depends(get_git_provider_service)]


# ==============================================================================
# Session Management Service
# ==============================================================================

def get_session_service(db: DBSession) -> SessionService:
    """
    Session service dependency.
    
    Creates a SessionService with database access for managing user sessions.
    """
    return SessionService(db)


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]


# ==============================================================================
# Authentication Service
# ==============================================================================

def get_auth_service(
    db: DBSession,
    git_provider_service: OAuthServiceDep,
    session_service: SessionServiceDep
) -> AuthService:
    """
    Auth service dependency with complete dependency chain.
    
    Creates an AuthService with Git Provider, Session services and DB session injected.
    This is an example of dependency composition in FastAPI.
    """
    return AuthService(
        db=db,
        git_provider_service=git_provider_service,
        session_service=session_service
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# ==============================================================================
# LLM Completion Service
# ==============================================================================

def get_chat_completion_service() -> ChatCompletionService:
    """
    Chat completion service dependency.
    
    Creates a ChatCompletionService for handling LLM operations.
    The service manages interactions with various LLM providers.
    
    Note: Currently ChatCompletionService creates its own ConfigService.
    TODO: Refactor to accept ConfigService as constructor parameter.
    """
    return ChatCompletionService()


ChatCompletionServiceDep = Annotated[ChatCompletionService, Depends(get_chat_completion_service)]


# ==============================================================================
# Repository Service
# ==============================================================================

def get_repo_service(
    config_service: ConfigServiceDep,
    repo_path: Path = Path("/tmp/repos")  # Default path
) -> RepoService:
    """
    Repository service dependency.
    
    Creates a RepoService for managing repository operations.
    The repo_path can be overridden per request if needed.
    
    TODO: Get default repo_path from ConfigService.
    """
    # In the future: repo_path = config_service.get_repo_config().default_path
    return RepoService(repo_path=repo_path)


RepoServiceDep = Annotated[RepoService, Depends(get_repo_service)]


# ==============================================================================
# Git Service
# ==============================================================================

def get_git_service(
    config_service: ConfigServiceDep,
    repo_path: Path = Path("/tmp/repos")  # Default path
) -> GitService:
    """
    Git service dependency.
    
    Creates a GitService for Git operations (commits, branches, PRs).
    
    TODO: Get default repo_path from ConfigService.
    """
    # In the future: repo_path = config_service.get_repo_config().default_path
    return GitService(repo_path=repo_path)


GitServiceDep = Annotated[GitService, Depends(get_git_service)]


# ==============================================================================
# LLM Provider Service
# ==============================================================================

def get_provider_service(
    config_service: ConfigServiceDep
) -> ProviderService:
    """
    LLM Provider service dependency.
    
    Creates a ProviderService with the configuration from ConfigService.
    Handles LLM provider and model operations.
    """
    return ProviderService(config_service=config_service)


ProviderServiceDep = Annotated[ProviderService, Depends(get_provider_service)]


# ==============================================================================
# Repository Locator Service
# ==============================================================================

def get_repo_locator_service(
    config_service: ConfigServiceDep,
    git_provider_service: OAuthServiceDep
) -> RepoLocatorService:
    """
    Repository locator service dependency.
    
    Creates a RepoLocatorService with config and Git Provider service injection.
    This service can handle both individual and organization hosting types
    dynamically based on the configuration and user context.
    """
    return RepoLocatorService(config_service.config, git_provider_service)


RepoLocatorServiceDep = Annotated[RepoLocatorService, Depends(get_repo_locator_service)]


# Note: For RepoLocatorService, it's often better to create it dynamically
# in the controller based on the hosting type.

# ==============================================================================
# Bearer Token Dependency
# ==============================================================================

async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise AuthenticationException(
            message="Authorization header required",
            context={"header": "Authorization"}
        )

    if not authorization.startswith("Bearer "):
        raise AuthenticationException(
            message="Invalid authorization header format",
            context={"expected_format": "Bearer <token>"}
        )

    return authorization.replace("Bearer ", "")


BearerTokenDep = Annotated[str, Depends(get_bearer_token)]