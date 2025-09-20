"""
API Dependencies
Common dependencies used across API endpoints
Following Dependency Injection pattern
"""
from typing import Generator
from sqlmodel import Session
from database.core import get_session
from services import create_oauth_service
from services.oauth.oauth_service import OAuthService
from services.auth.auth_service import AuthService

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Yields a database session and ensures proper cleanup.
    
    Usage in FastAPI endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    return get_session()


def get_oauth_service() -> OAuthService:
    """
    OAuth service dependency.
    Returns a configured OAuth service instance.
    
    Usage in FastAPI endpoints:
        @app.get("/auth/login")
        def login(oauth_service: OAuthService = Depends(get_oauth_service)):
            ...
    """
    return create_oauth_service()


def get_auth_service() -> AuthService:
    """
    Auth service dependency.
    Returns a configured Auth service instance.
    
    Usage in FastAPI endpoints:
        @app.post("/auth/logout")
        def logout(auth_service: AuthService = Depends(get_auth_service)):
            ...
    """
    oauth_service = create_oauth_service()
    return AuthService(oauth_service=oauth_service)