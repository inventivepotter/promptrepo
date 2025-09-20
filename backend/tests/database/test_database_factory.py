"""
Test suite for database factory and manager
Tests factory pattern implementation and singleton behavior
"""
import os
import pytest
from database.database_factory import DatabaseFactory, DatabaseManager
from database.database_adapter import SQLiteAdapter, PostgreSQLAdapter, MySQLAdapter


class TestDatabaseFactory:
    """Test cases for DatabaseFactory"""
    
    def test_factory_creates_sqlite_adapter(self):
        """Test factory creates SQLite adapter for sqlite URL"""
        sqlite_url = "sqlite:///test.db"
        adapter = DatabaseFactory.create_adapter(sqlite_url)
        
        assert isinstance(adapter, SQLiteAdapter)
        
        # Clean up if file was created
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def test_factory_creates_postgresql_adapter(self):
        """Test factory creates PostgreSQL adapter for postgresql URL"""
        postgres_url = "postgresql://localhost/test"
        adapter = DatabaseFactory.create_adapter(postgres_url)
        
        assert isinstance(adapter, PostgreSQLAdapter)
    
    def test_factory_handles_postgresql_variants(self):
        """Test factory handles different PostgreSQL URL schemes"""
        urls = [
            "postgresql://localhost/test",
            "postgresql+psycopg2://localhost/test",
            "postgresql+asyncpg://localhost/test",
            "postgres://localhost/test"
        ]
        
        for url in urls:
            adapter = DatabaseFactory.create_adapter(url)
            assert isinstance(adapter, PostgreSQLAdapter)
    
    def test_factory_creates_mysql_adapter(self):
        """Test factory creates MySQL adapter for mysql URL"""
        mysql_url = "mysql://localhost/test"
        adapter = DatabaseFactory.create_adapter(mysql_url)
        
        assert isinstance(adapter, MySQLAdapter)
    
    def test_factory_handles_mysql_variants(self):
        """Test factory handles different MySQL URL schemes"""
        urls = [
            "mysql://localhost/test",
            "mysql+pymysql://localhost/test",
            "mysql+mysqldb://localhost/test"
        ]
        
        for url in urls:
            adapter = DatabaseFactory.create_adapter(url)
            assert isinstance(adapter, MySQLAdapter)
    
    def test_factory_raises_error_for_unsupported_database(self):
        """Test factory raises ValueError for unsupported database types"""
        with pytest.raises(ValueError) as exc_info:
            DatabaseFactory.create_adapter("mongodb://localhost/test")
        
        assert "Unsupported database type: mongodb" in str(exc_info.value)
    
    def test_factory_echo_parameter(self):
        """Test factory passes echo parameter correctly"""
        adapter = DatabaseFactory.create_adapter("sqlite:///test.db", echo=True)
        assert adapter.echo is True
        
        adapter = DatabaseFactory.create_adapter("sqlite:///test.db", echo=False)
        assert adapter.echo is False
        
        # Clean up
        if os.path.exists("test.db"):
            os.remove("test.db")


class TestDatabaseManager:
    """Test cases for DatabaseManager singleton"""
    
    def teardown_method(self):
        """Reset manager after each test"""
        # Reset singleton instance
        DatabaseManager._instance = None
        DatabaseManager._adapter = None
    
    def test_manager_singleton_pattern(self):
        """Test DatabaseManager implements singleton pattern"""
        sqlite_url = "sqlite:///test_singleton.db"
        
        manager1 = DatabaseManager(sqlite_url, echo=False)
        manager2 = DatabaseManager(sqlite_url, echo=False)
        
        assert manager1 is manager2
        
        # Clean up
        if os.path.exists("test_singleton.db"):
            os.remove("test_singleton.db")
    
    def test_manager_adapter_initialization(self):
        """Test manager initializes adapter correctly"""
        sqlite_url = "sqlite:///test_manager.db"
        manager = DatabaseManager(sqlite_url, echo=False)
        
        assert manager.adapter is not None
        assert isinstance(manager.adapter, SQLiteAdapter)
        
        # Clean up
        if os.path.exists("test_manager.db"):
            os.remove("test_manager.db")
    
    def test_manager_raises_error_when_not_initialized(self):
        """Test manager raises error when accessed without initialization"""
        manager = DatabaseManager()
        
        with pytest.raises(RuntimeError) as exc_info:
            _ = manager.adapter
        
        assert "Database not initialized" in str(exc_info.value)
    
    def test_manager_reset(self):
        """Test manager reset functionality"""
        sqlite_url = "sqlite:///test_reset.db"
        manager = DatabaseManager(sqlite_url, echo=False)
        
        # Verify manager is initialized
        assert manager.adapter is not None
        
        # Reset manager
        manager.reset()
        
        # After reset, singleton should be cleared
        new_manager = DatabaseManager(sqlite_url, echo=False)
        assert new_manager is not manager
        
        # Clean up
        if os.path.exists("test_reset.db"):
            os.remove("test_reset.db")
    
    def test_manager_initialize_method(self):
        """Test manager can be initialized with initialize method"""
        manager = DatabaseManager()
        
        # Initially not initialized
        with pytest.raises(RuntimeError):
            _ = manager.adapter
        
        # Initialize with URL
        manager.initialize("sqlite:///test_init.db", echo=False)
        
        # Now should work
        assert manager.adapter is not None
        assert isinstance(manager.adapter, SQLiteAdapter)
        
        # Clean up
        if os.path.exists("test_init.db"):
            os.remove("test_init.db")