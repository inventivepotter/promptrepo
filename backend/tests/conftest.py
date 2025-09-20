"""
Root configuration for pytest tests.
Creates a fresh in-memory SQLite database for each test.
"""
import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event

@pytest.fixture(autouse=True)
def db_engine():
    """Create a fresh database engine for each test."""
    # Create a new engine for each test
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Clear metadata and create fresh tables for each test
    SQLModel.metadata.clear()
    
    # Import models
    from models.user import User
    from models.user_sessions import UserSessions
    from models.user_repos import UserRepos, RepoStatus
    from models.user_llm_configs import UserLLMConfigs
    
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    yield test_engine
    
    # Clean up after test
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()

@pytest.fixture
def db_session(db_engine):
    """
    Provides a database session for each test.
    Database is already fresh for each test via db_engine fixture.
    """
    with Session(db_engine) as session:
        yield session