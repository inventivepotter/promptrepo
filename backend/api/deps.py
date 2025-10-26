"""
API Dependencies
Common dependencies used across API endpoints following FastAPI best practices.

This module provides centralized dependency injection for all services.
We use function-based dependencies as recommended by FastAPI documentation.
"""
from typing import Generator, Annotated, Optional
from fastapi import Depends, Header, Cookie, Request
from huggingface_hub import User
from sqlmodel import Session
from pathlib import Path
import logging
from database.models.user_sessions import UserSessions
from middlewares.rest import AuthenticationException
from utils.cookie import get_session_from_cookie

# Set up logger
logger = logging.getLogger(__name__)

from database.core import get_session
from services.auth.auth_service import AuthService
from services.auth.session_service import SessionService
from services.config.config_service import ConfigService
from schemas.hosting_type_enum import HostingType
from services.llm.completion_service import ChatCompletionService
from services.llm.llm_provider_service import LLMProviderService
from services.local_repo.git_service import GitService
from services.local_repo.local_repo_service import LocalRepoService
from services.remote_repo.remote_repo_service import RemoteRepoService
from services.prompt.prompt_service import PromptService
from services.file_operations.file_operations_service import FileOperationsService
from services.tool import ToolService
from services.tool.tool_execution_service import ToolExecutionService


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
    config_service: ConfigServiceDep,
    session_service: SessionServiceDep
) -> AuthService:
    """
    Auth service dependency with complete dependency chain.
    
    Creates an AuthService with Git Provider, Session services and DB session injected.
    This is an example of dependency composition in FastAPI.
    """
    return AuthService(
        db=db,
        config_service=config_service,
        session_service=session_service
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# ==============================================================================
# LLM Completion Service
# ==============================================================================

def get_chat_completion_service(
    config_service: ConfigServiceDep
) -> ChatCompletionService:
    """
    Chat completion service dependency.
    
    Creates a ChatCompletionService for handling LLM operations.
    The service manages interactions with various LLM providers.
    Uses proper dependency injection with ConfigService.
    Note: ToolService is injected at the endpoint level to avoid circular dependencies.
    """
    return ChatCompletionService(config_service=config_service)


ChatCompletionServiceDep = Annotated[ChatCompletionService, Depends(get_chat_completion_service)]


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
) -> LLMProviderService:
    """
    LLM Provider service dependency.
    
    Creates a ProviderService with the configuration from ConfigService.
    Handles LLM provider and model operations.
    """
    return LLMProviderService(config_service=config_service)


ProviderServiceDep = Annotated[LLMProviderService, Depends(get_provider_service)]


# ==============================================================================
# Repository Locator Service
# ==============================================================================

def get_remote_repo_service(
    db: DBSession
) -> RemoteRepoService:
    """
    Remote repository service dependency.
    
    Creates a RemoteRepoService with database session, config, and session service injection.
    This service can handle both individual and organization hosting types
    dynamically based on the configuration and user context.
    """
    return RemoteRepoService(db=db)


RemoteRepoServiceDep = Annotated[RemoteRepoService, Depends(get_remote_repo_service)]


# ==============================================================================
# File Operations Service (Singleton)
# ==============================================================================

# Create a singleton instance of FileOperationsService
# This service is stateless and can be safely shared across all requests
_file_operations_service: FileOperationsService | None = None


def get_file_operations_service() -> FileOperationsService:
    """
    File operations service dependency (singleton).
    
    Returns a shared instance of FileOperationsService for file I/O operations.
    This is a stateless utility service that doesn't need per-request instances.
    """
    global _file_operations_service
    if _file_operations_service is None:
        _file_operations_service = FileOperationsService()
    return _file_operations_service


FileOperationsServiceDep = Annotated[FileOperationsService, Depends(get_file_operations_service)]


# ==============================================================================
# Local Repository Service
# ==============================================================================

def get_local_repo_service(
    config_service: ConfigServiceDep,
    db: DBSession,
    remote_repo_service: RemoteRepoServiceDep
) -> LocalRepoService:
    """
    Local repository service dependency.
    
    Creates a LocalRepoService for handling git workflow operations and PR creation.
    """
    return LocalRepoService(
        config_service=config_service,
        db=db,
        remote_repo_service=remote_repo_service
    )


LocalRepoServiceDep = Annotated[LocalRepoService, Depends(get_local_repo_service)]


# ==============================================================================
# Prompt Service
# ==============================================================================

def get_prompt_service(
    config_service: ConfigServiceDep,
    file_ops_service: FileOperationsServiceDep,
    local_repo_service: LocalRepoServiceDep
) -> PromptService:
    """
    Prompt service dependency.
    
    Creates a PromptService with all required dependencies injected.
    The service handles both individual and organization hosting types.
    """
    return PromptService(
        config_service=config_service.config,
        file_ops_service=file_ops_service,
        local_repo_service=local_repo_service
    )


PromptServiceDep = Annotated[PromptService, Depends(get_prompt_service)]


# ==============================================================================
# Tool Service
# ==============================================================================

def get_tool_service(
    config_service: ConfigServiceDep,
    local_repo_service: LocalRepoServiceDep,
    file_operations_service: FileOperationsServiceDep
) -> ToolService:
    """
    Tool service dependency.
    
    Creates a ToolService for managing tool definitions.
    """
    return ToolService(
        config_service=config_service.config,
        local_repo_service=local_repo_service,
        file_operations_service=file_operations_service
    )


ToolServiceDep = Annotated[ToolService, Depends(get_tool_service)]


# ==============================================================================
# Tool Execution Service
# ==============================================================================

def get_tool_execution_service(
    tool_service: ToolServiceDep,
    chat_completion_service: ChatCompletionServiceDep
) -> ToolExecutionService:
    """
    Tool execution service dependency.
    
    Creates a ToolExecutionService for handling tool call loops and responses.
    """
    return ToolExecutionService(
        tool_service=tool_service,
        chat_completion_service=chat_completion_service
    )


ToolExecutionServiceDep = Annotated[ToolExecutionService, Depends(get_tool_execution_service)]


# Note: For RemoteRepoService, it's often better to create it dynamically
# in the controller based on the hosting type.

# ==============================================================================
# Bearer Token Dependency
# ==============================================================================

async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise AuthenticationException(
            message="Unauthorized Access",
            detail="Please login to access this resource",
            context={"header": "Authorization"}
        )

    if not authorization.startswith("Bearer "):
        raise AuthenticationException(
            message="Invalid authorization header format",
            context={"expected_format": "Bearer <token>"}
        )

    return authorization.replace("Bearer ", "")


BearerTokenDep = Annotated[str, Depends(get_bearer_token)]


# ==============================================================================
# Session Cookie Dependency
# ==============================================================================

async def get_session_cookie(request: Request) -> str | None:
    """Extract and decrypt session token from HttpOnly cookie."""
    session_id = await get_session_from_cookie(request)
    if not session_id:
        raise AuthenticationException(
            message="Unauthorized Access",
            detail="Please login to access this resource",
            context={"cookie": "sessionId"}
        )
    return session_id


SessionCookieDep = Annotated[str, Depends(get_session_cookie)]


# ==============================================================================
# Authentication Dependencies
# ==============================================================================

# User ID to use when hosting type is INDIVIDUAL
INDIVIDUAL_USER_ID = "individual-user"


async def get_current_user(
    session_service: SessionServiceDep,
    config_service: ConfigServiceDep,
    session_id: SessionCookieDep
) -> str:
    """
    Get current authenticated user.
    
    Validates session cookie, returns user_id or raises HTTPException.
    Handles INDIVIDUAL hosting type by returning INDIVIDUAL_USER_ID.
    
    Returns:
        str: User ID for authenticated user
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # Check hosting type first
    try:
        hosting_type = config_service.get_hosting_config().type
        if hosting_type == HostingType.INDIVIDUAL:
            return INDIVIDUAL_USER_ID
    except Exception as e:
        logger.warning(f"Failed to get hosting type: {e}")
    
    user_session = session_service.is_session_valid(session_id)
    if not user_session:
        raise AuthenticationException(
            message="Authentication Required",
            detail="Your session has expired or could not be found. Please sign in again",
            context={"user_action": "session_invalid"}
        )
    
    return user_session.user_id

async def get_current_session(
    session_service: SessionServiceDep,
    session_id: SessionCookieDep
) -> UserSessions:
    """
    Get current authenticated user.
    
    Validates session cookie, returns user_id or raises HTTPException.
    Handles INDIVIDUAL hosting type by returning INDIVIDUAL_USER_ID.
    
    Returns:
        str: User ID for authenticated user
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    user_session = session_service.is_session_valid(session_id)
    if not user_session:
        raise AuthenticationException(
            message="Authentication Required",
            detail="Your session has expired or could not be found. Please sign in again",
            context={"user_action": "session_invalid"}
        )
    return user_session


async def get_optional_user(
    session_service: SessionServiceDep,
    config_service: ConfigServiceDep,
    request: Request
) -> Optional[str]:
    """
    Get current user if authenticated, return None otherwise.
    
    Similar to get_current_user but doesn't raise exceptions for missing auth.
    Useful for endpoints that work with or without authentication.
    
    Returns:
        Optional[str]: User ID if authenticated, None otherwise
    """
    # Check hosting type first
    try:
        hosting_type = config_service.get_hosting_config().type
        if hosting_type == HostingType.INDIVIDUAL:
            return INDIVIDUAL_USER_ID
    except Exception as e:
        logger.warning(f"Failed to get hosting type: {e}")
    
    # If no session cookie, return None
    session_id = await get_session_from_cookie(request)
    if not session_id:
        return None
    
    # Validate session
    if not session_service.is_session_valid(session_id):
        return None
    
    # Get session and user
    user_session = session_service.get_session_by_id(session_id)
    if not user_session:
        return None
    
    return user_session.user_id


# Type aliases for authentication dependencies
CurrentUserDep = Annotated[str, Depends(get_current_user)]
CurrentSessionDep = Annotated[UserSessions, Depends(get_current_session)]
OptionalUserDep = Annotated[Optional[str], Depends(get_optional_user)]