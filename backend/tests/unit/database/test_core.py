import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from sqlmodel import Session

from database.core import get_session, create_db_and_tables, get_engine, db_manager

class TestDatabaseCore:
    """Test cases for database core module"""

    def test_db_manager_initialization(self):
        """Test that db_manager is properly initialized"""
        assert db_manager is not None
        assert hasattr(db_manager, 'adapter')
        assert hasattr(db_manager, 'engine')

    def test_get_session(self):
        """Test get_session function returns a valid session generator"""
        session_gen = get_session()
        
        # Should return a generator
        assert hasattr(session_gen, '__iter__')
        
        # Get the session from generator
        session = next(session_gen)
        
        # Should be a valid SQLModel Session
        assert isinstance(session, Session)
        assert session.bind is not None
        
        # Close the generator properly
        try:
            next(session_gen)  # Should raise StopIteration
        except StopIteration:
            pass  # Expected

    def test_get_engine(self):
        """Test get_engine function returns the database engine"""
        engine = get_engine()
        assert engine is not None
        assert engine is db_manager.engine

    @patch('database.core.db_manager')
    def test_create_db_and_tables(self, mock_db_manager):
        """Test create_db_and_tables function calls db_manager.create_tables"""
        create_db_and_tables()
        
        # Verify that create_tables was called on the db_manager
        mock_db_manager.create_tables.assert_called_once()

    def test_db_manager_singleton(self):
        """Test that db_manager is a singleton instance"""
        from database.core import db_manager as db_manager1
        from database.core import db_manager as db_manager2
        
        # Both references should point to the same instance
        assert db_manager1 is db_manager2

    def test_db_manager_with_sqlite_memory(self):
        """Test db_manager works with in-memory SQLite database"""
        # Create a temporary in-memory database URL
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            # Create a new db_manager with test database
            from database.database_factory import DatabaseManager
            test_manager = DatabaseManager(
                database_url=f"sqlite:///{test_db}",
                echo=False
            )
            
            # Test that we can get a session
            session_gen = test_manager.get_session()
            session = next(session_gen)
            
            # Should be a valid session
            assert isinstance(session, Session)
            assert session.bind is not None
            
            # Close the generator
            try:
                next(session_gen)
            except StopIteration:
                pass
            
            # Test that we can create tables
            test_manager.create_tables()
            
            # Verify engine is accessible
            assert test_manager.engine is not None
        finally:
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)

    @patch('database.core.settings')
    def test_db_manager_initialization_with_settings(self, mock_settings):
        """Test db_manager is initialized with correct settings"""
        # Mock settings
        mock_settings.database_url = "sqlite:///:memory:"
        mock_settings.database_echo = False
        
        # Add logging to debug the issue
        print(f"Mock settings database_url: {mock_settings.database_url}")
        print(f"Mock settings database_echo: {mock_settings.database_echo}")
        
        # Re-import to test initialization with mocked settings
        import importlib
        from database import core
        
        # Log the state before reload
        print(f"Before reload - db_manager id: {id(core.db_manager)}")
        print(f"Before reload - adapter exists: {hasattr(core.db_manager, '_adapter') and core.db_manager._adapter is not None}")
        if hasattr(core.db_manager, '_adapter') and core.db_manager._adapter is not None:
            print(f"Before reload - current database_url: {core.db_manager.adapter.database_url}")
        
        # Reset the db_manager to clear the singleton instance before reload
        core.db_manager.reset()
        
        importlib.reload(core)
        
        # Log the state after reload
        print(f"After reload - db_manager id: {id(core.db_manager)}")
        print(f"After reload - adapter exists: {hasattr(core.db_manager, '_adapter') and core.db_manager._adapter is not None}")
        if hasattr(core.db_manager, '_adapter') and core.db_manager._adapter is not None:
            print(f"After reload - current database_url: {core.db_manager.adapter.database_url}")
            print(f"After reload - current database_echo: {core.db_manager.adapter.echo}")
        
        # Verify db_manager was initialized with mocked settings
        assert core.db_manager.adapter.database_url == "sqlite:///:memory:"
        assert core.db_manager.adapter.echo is False

    def test_multiple_sessions(self):
        """Test creating multiple sessions"""
        # Get two separate sessions
        session_gen1 = get_session()
        session1 = next(session_gen1)
        
        session_gen2 = get_session()
        session2 = next(session_gen2)
        
        # Should be different session instances
        assert session1 is not session2
        
        # But both should be valid sessions
        assert isinstance(session1, Session)
        assert isinstance(session2, Session)
        
        # Close generators
        try:
            next(session_gen1)
            next(session_gen2)
        except StopIteration:
            pass  # Expected

    @patch('builtins.print')
    @patch('database.core.db_manager')
    def test_create_db_and_tables_prints_success(self, mock_db_manager, mock_print):
        """Test create_db_and_tables prints success message"""
        create_db_and_tables()
        
        # Verify create_tables was called
        mock_db_manager.create_tables.assert_called_once()
        
        # Verify success message was printed
        mock_print.assert_called_with("Database tables created successfully")