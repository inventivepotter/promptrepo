"""
Core database module that initializes the database connection
using the adapter pattern based on the DATABASE_URL
"""
from typing import Generator
from sqlmodel import Session as SQLSession
from .database_factory import DatabaseManager
from settings.settings import settings


# Initialize the database manager singleton with settings
db_manager = DatabaseManager(
    database_url=settings.database_url,
    echo=settings.database_echo
)

def get_session() -> Generator[SQLSession, None, None]:
    """
    Dependency to get database session.
    Used in FastAPI dependency injection.
    """
    return db_manager.get_session()

def create_db_and_tables() -> None:
    """
    Create all database tables.
    Should be called on application startup.
    """
    # Import database.models to register them with SQLModel before creating tables
    from database.models import User, UserSessions, UserRepos
    
    db_manager.create_tables()
    print("Database tables created successfully")

def get_engine():
    """
    Get the database engine instance.
    Useful for direct database operations.
    """
    return db_manager.engine

# Re-export for convenience
__all__ = [
    'db_manager',
    'get_session',
    'create_db_and_tables',
    'get_engine'
]