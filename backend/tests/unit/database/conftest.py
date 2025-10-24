"""
Configuration for database tests.
This extends the root conftest with database-specific fixtures.
"""
import pytest
from sqlmodel import SQLModel, Session
from unittest.mock import MagicMock

# Models are imported and registered in the root conftest.py's db_engine fixture.
# Importing them here again can cause 'table already defined' errors during pytest's
# collection phase. The db_session fixture from the root conftest is inherited.


@pytest.fixture
def mock_db_manager():
    """Mock database manager fixture for testing database core functionality"""
    mock_manager = MagicMock()
    mock_adapter = MagicMock()
    mock_engine = MagicMock()
    
    # Set up the mock relationships
    mock_manager.adapter = mock_adapter
    mock_manager.engine = mock_engine
    mock_adapter.engine = mock_engine
    mock_adapter.database_url = "sqlite:///:memory:"
    mock_adapter.echo = False
    
    # Mock the get_session method to return a proper session generator
    def mock_get_session():
        # Create a real session for testing
        from database.database_factory import DatabaseManager
        test_manager = DatabaseManager(database_url="sqlite:///:memory:", echo=False)
        return test_manager.get_session()
    
    mock_manager.get_session = mock_get_session
    mock_manager.create_tables = MagicMock()
    
    return mock_manager