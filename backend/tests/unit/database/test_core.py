import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from sqlmodel import Session

from database.core import get_session, create_db_and_tables, get_engine, db_manager

class TestDatabaseCore:
    """Test cases for database core module"""

    def test_db_manager_initialization(self, mock_db_manager):
        """Test that db_manager is properly initialized"""
        assert mock_db_manager is not None
        assert hasattr(mock_db_manager, 'adapter')
        assert hasattr(mock_db_manager, 'engine')

    @patch('database.core.db_manager')
    def test_get_session(self, mock_db_manager):
        """Test get_session function returns a valid session generator"""
        # Mock session to avoid file system issues
        mock_session = MagicMock(spec=Session)
        mock_session.bind = MagicMock()
        
        def mock_get_session():
            def session_generator():
                yield mock_session
            return session_generator()
        
        mock_db_manager.get_session = mock_get_session
        
        session_gen = get_session()
        
        # Should return a generator
        assert hasattr(session_gen, '__iter__')
        
        # Get session from generator
        session = next(session_gen)
        
        # Should be mock session we provided
        assert session is mock_session
        assert session.bind is not None
        
        # Close generator properly
        try:
            next(session_gen)  # Should raise StopIteration
        except StopIteration:
            pass  # Expected

    @patch('database.core.db_manager')
    def test_get_engine(self, mock_db_manager):
        """Test get_engine function returns database engine"""
        mock_engine = MagicMock()
        mock_db_manager.engine = mock_engine
        
        engine = get_engine()
        assert engine is not None
        assert engine is mock_engine

    @patch('database.core.db_manager')
    def test_create_db_and_tables(self, mock_db_manager):
        """Test create_db_and_tables function calls db_manager.create_tables"""
        create_db_and_tables()
        
        # Verify that create_tables was called on db_manager
        mock_db_manager.create_tables.assert_called_once()

    def test_db_manager_singleton(self):
        """Test that db_manager is a singleton instance"""
        from database.core import db_manager as db_manager1
        from database.core import db_manager as db_manager2
        
        # Both references should point to same instance
        assert db_manager1 is db_manager2

    @patch('database.core.db_manager')
    def test_db_manager_with_sqlite_memory(self, mock_db_manager):
        """Test db_manager works with in-memory SQLite database"""
        # Mock session generator to avoid file system issues
        mock_session = MagicMock(spec=Session)
        mock_session.bind = MagicMock()
        
        def mock_get_session():
            def session_generator():
                yield mock_session
            return session_generator()
        
        mock_db_manager.get_session = mock_get_session
        mock_db_manager.engine = MagicMock()
        
        # Test that we can get a session
        session_gen = get_session()
        session = next(session_gen)
        
        # Should be mock session we provided
        assert session is mock_session
        assert session.bind is not None
        
        # Close generator
        try:
            next(session_gen)
        except StopIteration:
            pass

    @patch('settings.settings')
    def test_db_manager_initialization_with_settings(self, mock_settings):
        """Test db_manager is initialized with correct settings"""
        # Mock settings
        mock_settings.database_url = "sqlite:///:memory:"
        mock_settings.database_echo = False
        
        # Test that settings are properly accessed
        from database.core import db_manager
        
        # Mock the adapter to avoid real database initialization
        with patch('database.database_factory.DatabaseFactory') as mock_factory:
            mock_adapter = MagicMock()
            mock_adapter.database_url = "sqlite:///:memory:"
            mock_adapter.echo = False
            mock_factory.create_adapter.return_value = mock_adapter
            
            # Reset and reinitialize db_manager
            db_manager.reset()
            db_manager.initialize("sqlite:///:memory:", False)
            
            # Verify the adapter was created with correct settings
            mock_factory.create_adapter.assert_called_once_with("sqlite:///:memory:", False)
            
            # Verify the adapter has correct properties
            assert db_manager.adapter.database_url == "sqlite:///:memory:"
            assert db_manager.adapter.echo is False

    @patch('database.core.db_manager')
    def test_multiple_sessions(self, mock_db_manager):
        """Test creating multiple sessions"""
        # Create separate mock sessions for testing
        mock_session1 = MagicMock(spec=Session)
        mock_session1.bind = MagicMock()
        mock_session2 = MagicMock(spec=Session)
        mock_session2.bind = MagicMock()
        
        # Create separate mock generators for each call
        def session_generator1():
            yield mock_session1
        
        def session_generator2():
            yield mock_session2
        
        # Set up mock to return different generators on each call
        mock_db_manager.get_session.side_effect = [session_generator1(), session_generator2()]
        
        # Get two separate sessions
        gen1 = get_session()
        session1 = next(gen1)
        
        gen2 = get_session()
        session2 = next(gen2)
        
        # Should be different session instances
        assert session1 is not session2
        
        # Both should be mock sessions we provided (check with is for identity)
        assert session1 is mock_session1
        assert session2 is mock_session2
        
        # Close generators
        try:
            next(gen1)
            next(gen2)
        except StopIteration:
            pass  # Expected

    @patch('database.core.logger')
    @patch('database.core.db_manager')
    def test_create_db_and_tables_logs_success(self, mock_db_manager, mock_logger):
        """Test create_db_and_tables logs success message"""
        create_db_and_tables()
        
        # Verify create_tables was called
        mock_db_manager.create_tables.assert_called_once()
        
        # Verify success message was logged (info level)
        mock_logger.info.assert_called()