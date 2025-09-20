"""
API Dependencies
Common dependencies used across API endpoints
Following Dependency Injection pattern
"""
from typing import Generator
from sqlmodel import Session
from database.core import get_session

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