"""
Test suite for database adapters
Tests SQLite, PostgreSQL, and MySQL adapter implementations
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from sqlmodel import select
from database.database_adapter import SQLiteAdapter, PostgreSQLAdapter, MySQLAdapter
from database.models.user import User


class TestSQLiteAdapter:
    """Test cases for SQLite adapter"""
    
    def test_sqlite_adapter_creation(self):
        """Test SQLite adapter can be created"""
        sqlite_url = "sqlite:///test_sqlite.db"
        adapter = SQLiteAdapter(sqlite_url, echo=False)
        
        assert adapter is not None
        assert adapter.database_url == sqlite_url
        assert adapter.echo is False
    
    def test_sqlite_adapter_creation_with_memory_db(self):
        """Test SQLite adapter can be created with in-memory database"""
        sqlite_url = "sqlite:///:memory:"
        adapter = SQLiteAdapter(sqlite_url, echo=True)
        
        assert adapter is not None
        assert adapter.database_url == sqlite_url
        assert adapter.echo is True
    
    def test_sqlite_adapter_creation_with_relative_path(self):
        """Test SQLite adapter with relative path"""
        sqlite_url = "sqlite:///./test_relative.db"
        adapter = SQLiteAdapter(sqlite_url)
        
        assert adapter is not None
        assert adapter.database_url == sqlite_url
    
    def test_sqlite_connection_args(self):
        """Test SQLite returns correct connection arguments"""
        adapter = SQLiteAdapter("sqlite:///test.db")
        args = adapter.get_connection_args()
        
        assert args == {"check_same_thread": False}
    
    def test_sqlite_database_preparation(self):
        """Test SQLite creates database file"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            sqlite_url = f"sqlite:///{test_db}"
            adapter = SQLiteAdapter(sqlite_url, echo=False)
            
            # Prepare database (should create file)
            adapter.prepare_database()
            
            # Check file exists
            assert os.path.exists(test_db)
        finally:
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)
    
    def test_sqlite_database_preparation_memory_db(self):
        """Test SQLite prepare_database with in-memory database"""
        sqlite_url = "sqlite:///:memory:"
        adapter = SQLiteAdapter(sqlite_url, echo=False)
        
        # Should not raise error for in-memory database
        adapter.prepare_database()
    
    def test_sqlite_table_creation(self):
        """Test SQLite can create tables"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            sqlite_url = f"sqlite:///{test_db}"
            adapter = SQLiteAdapter(sqlite_url, echo=False)
            
            # Create tables
            adapter.create_tables()
            
            # Test session creation
            for session in adapter.get_session():
                # Try to query (tables should exist)
                users = session.exec(select(User)).all()
                assert users == []
        finally:
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)
    
    def test_sqlite_session_context_manager(self):
        """Test SQLite session context manager handles exceptions"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            sqlite_url = f"sqlite:///{test_db}"
            adapter = SQLiteAdapter(sqlite_url, echo=False)
            adapter.create_tables()
            
            # Test session context manager
            session_generator = adapter.get_session()
            session = next(session_generator)
            
            # Session should be active
            assert session.is_active is True
            
            # Close generator properly
            session_generator.close()
        finally:
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)
    
    def test_sqlite_invalid_url(self):
        """Test SQLite adapter handles invalid paths during prepare_database"""
        adapter = SQLiteAdapter("sqlite:////root/no_permission/db.db")
        assert adapter is not None
        
        # Should fail when trying to prepare database in restricted location
        with pytest.raises((PermissionError, OSError)):
            adapter.prepare_database()


class TestPostgreSQLAdapter:
    """Test cases for PostgreSQL adapter"""
    
    def test_postgresql_adapter_creation(self):
        """Test PostgreSQL adapter can be created"""
        postgres_url = "postgresql://user:pass@localhost:5432/testdb"
        adapter = PostgreSQLAdapter(postgres_url, echo=False)
        
        assert adapter is not None
        assert adapter.database_url == postgres_url
        assert adapter.echo is False
    
    def test_postgresql_adapter_creation_with_different_schemes(self):
        """Test PostgreSQL adapter with different URL schemes"""
        urls = [
            "postgresql://user:pass@localhost:5432/testdb",
            "postgresql+psycopg2://user:pass@localhost:5432/testdb",
            "postgresql+asyncpg://user:pass@localhost:5432/testdb",
            "postgres://user:pass@localhost:5432/testdb"
        ]
        
        for url in urls:
            adapter = PostgreSQLAdapter(url, echo=True)
            assert adapter is not None
            assert adapter.database_url == url
            assert adapter.echo is True
    
    def test_postgresql_connection_args(self):
        """Test PostgreSQL returns correct connection arguments"""
        adapter = PostgreSQLAdapter("postgresql://localhost/test")
        args = adapter.get_connection_args()
        
        assert args["pool_size"] == 10
        assert args["max_overflow"] == 20
        assert args["pool_pre_ping"] is True
        assert args["pool_recycle"] == 3600
    
    def test_postgresql_connection_args_custom(self):
        """Test PostgreSQL connection args are fixed values"""
        adapter = PostgreSQLAdapter("postgresql://localhost/test")
        args = adapter.get_connection_args()
        
        # PostgreSQL adapter uses fixed values
        assert args["pool_size"] == 10
        assert args["max_overflow"] == 20
        assert args["pool_recycle"] == 3600
        assert args["pool_pre_ping"] is True
    
    @patch('database.database_adapter.create_engine')
    @patch('sqlmodel.SQLModel.metadata.create_all')
    def test_postgresql_create_tables(self, mock_create_all, mock_create_engine):
        """Test PostgreSQL create_tables method"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        adapter = PostgreSQLAdapter("postgresql://localhost/test")
        adapter.create_tables()
        
        # Verify create_engine was called
        mock_create_engine.assert_called_once()
        # Verify SQLModel.metadata.create_all was called
        mock_create_all.assert_called_once_with(mock_engine)
    
    @patch('database.database_adapter.create_engine')
    def test_postgresql_get_session(self, mock_create_engine):
        """Test PostgreSQL get_session method"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        with patch('database.database_adapter.SQLSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            adapter = PostgreSQLAdapter("postgresql://localhost/test")
            session_generator = adapter.get_session()
            session = next(session_generator)
            
            # Verify Session class was called with the engine
            mock_session_class.assert_called_with(mock_engine)
            # Verify session generator returns a session
            assert session is not None
    
    def test_postgresql_invalid_url(self):
        """Test PostgreSQL adapter with invalid URL format"""
        # Should not raise error during creation, but might fail during connection
        adapter = PostgreSQLAdapter("postgresql://invalid-url-without-port/test")
        assert adapter is not None


class TestMySQLAdapter:
    """Test cases for MySQL adapter"""
    
    def test_mysql_adapter_creation(self):
        """Test MySQL adapter can be created"""
        mysql_url = "mysql://user:pass@localhost:3306/testdb"
        adapter = MySQLAdapter(mysql_url, echo=False)
        
        assert adapter is not None
        assert adapter.database_url == mysql_url
        assert adapter.echo is False
    
    def test_mysql_adapter_creation_with_different_schemes(self):
        """Test MySQL adapter with different URL schemes"""
        urls = [
            "mysql://user:pass@localhost:3306/testdb",
            "mysql+pymysql://user:pass@localhost:3306/testdb",
            "mysql+mysqldb://user:pass@localhost:3306/testdb"
        ]
        
        for url in urls:
            adapter = MySQLAdapter(url, echo=True)
            assert adapter is not None
            assert adapter.database_url == url
            assert adapter.echo is True
    
    def test_mysql_connection_args(self):
        """Test MySQL returns correct connection arguments"""
        adapter = MySQLAdapter("mysql://localhost/test")
        args = adapter.get_connection_args()
        
        assert args["pool_size"] == 10
        assert args["max_overflow"] == 20
        assert args["pool_pre_ping"] is True
        assert args["pool_recycle"] == 3600
    
    def test_mysql_connection_args_custom(self):
        """Test MySQL connection args are fixed values"""
        adapter = MySQLAdapter("mysql://localhost/test")
        args = adapter.get_connection_args()
        
        # MySQL adapter uses fixed values
        assert args["pool_size"] == 10
        assert args["max_overflow"] == 20
        assert args["pool_recycle"] == 3600
        assert args["pool_pre_ping"] is True
    
    @patch('database.database_adapter.create_engine')
    @patch('sqlmodel.SQLModel.metadata.create_all')
    def test_mysql_create_tables(self, mock_create_all, mock_create_engine):
        """Test MySQL create_tables method"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        adapter = MySQLAdapter("mysql://localhost/test")
        adapter.create_tables()
        
        # Verify create_engine was called
        mock_create_engine.assert_called_once()
        # Verify SQLModel.metadata.create_all was called
        mock_create_all.assert_called_once_with(mock_engine)
    
    @patch('database.database_adapter.create_engine')
    def test_mysql_get_session(self, mock_create_engine):
        """Test MySQL get_session method"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        with patch('database.database_adapter.SQLSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            adapter = MySQLAdapter("mysql://localhost/test")
            session_generator = adapter.get_session()
            session = next(session_generator)
            
            # Verify Session class was called with the engine
            mock_session_class.assert_called_with(mock_engine)
            # Verify session generator returns a session
            assert session is not None
    
    def test_mysql_invalid_url(self):
        """Test MySQL adapter with invalid URL format"""
        # Should not raise error during creation, but might fail during connection
        adapter = MySQLAdapter("mysql://invalid-url-without-port/test")
        assert adapter is not None


class TestDatabaseAdapterCommon:
    """Test cases common to all database adapters"""
    