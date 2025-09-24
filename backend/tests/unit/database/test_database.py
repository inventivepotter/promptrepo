"""
Test suite for database adapter pattern implementation
Tests both SQLite and PostgreSQL adapters using pytest conventions
"""
import pytest
import os
from database.database_factory import DatabaseFactory, DatabaseManager
from database.models.user import User


class TestDatabaseAdapterPattern:
    """Test cases for database adapter pattern implementation"""
    
    def teardown_method(self):
        """Clean up after each test method"""
        # Reset singleton instance
        DatabaseManager._instance = None
        DatabaseManager._adapter = None
    
    def test_sqlite_adapter_creation_and_operations(self, db_session):
        """Test SQLite adapter creation and basic operations"""
        # Create SQLite adapter
        sqlite_url = "sqlite:///:memory:"
        adapter = DatabaseFactory.create_adapter(sqlite_url, echo=False)
        
        # Create tables
        adapter.create_tables()
        
        # Test session creation
        for session in adapter.get_session():
            # Create test user
            test_user = User(
                oauth_username="test_user",
                oauth_name="Test User",
                oauth_email="test@example.com",
                oauth_provider="github",
                oauth_user_id=12345
            )
            session.add(test_user)
            session.commit()
            
            # Verify user was created
            saved_user = session.query(User).filter_by(username="test_user").first()
            assert saved_user is not None
            assert saved_user.username == "test_user"
            assert saved_user.email == "test@example.com"
            
            # Clean up
            session.delete(test_user)
            session.commit()
    
    def test_postgresql_adapter_creation(self):
        """Test PostgreSQL adapter creation (without actual connection)"""
        postgres_url = "postgresql://user:password@localhost:5432/testdb"
        
        # Should create adapter without error
        adapter = DatabaseFactory.create_adapter(postgres_url, echo=False)
        assert adapter is not None
        assert adapter.database_url == postgres_url
        assert adapter.echo is False
    
    def test_database_manager_singleton_pattern(self):
        """Test DatabaseManager singleton pattern"""
        sqlite_url = "sqlite:///test_singleton.db"
        
        # Create two instances
        manager1 = DatabaseManager(sqlite_url, echo=False)
        manager2 = DatabaseManager(sqlite_url, echo=False)
        
        # Verify singleton
        assert manager1 is manager2
        
        # Test table creation
        manager1.create_tables()
        
        # Clean up
        if os.path.exists("test_singleton.db"):
            os.remove("test_singleton.db")
        
        # Reset manager
        manager1.reset()
    
    def test_database_manager_singleton_with_different_urls(self):
        """Test DatabaseManager singleton with different URLs"""
        url1 = "sqlite:///test1.db"
        url2 = "sqlite:///test2.db"
        
        # Create manager with first URL
        manager1 = DatabaseManager(url1, echo=False)
        
        # Create manager with second URL - should return same instance
        manager2 = DatabaseManager(url2, echo=False)
        
        # Should still be the same instance (singleton)
        assert manager1 is manager2
        
        # Clean up
        for db_file in ["test1.db", "test2.db"]:
            if os.path.exists(db_file):
                os.remove(db_file)
        
        manager1.reset()
    
    def test_unsupported_database_type(self):
        """Test error handling for unsupported database types"""
        unsupported_url = "mongodb://localhost:27017/testdb"
        
        with pytest.raises(ValueError) as exc_info:
            DatabaseFactory.create_adapter(unsupported_url)
        
        assert "Unsupported database type: mongodb" in str(exc_info.value)
    
    def test_adapter_echo_parameter(self):
        """Test adapter echo parameter"""
        sqlite_url = "sqlite:///:memory:"
        
        # Test with echo=True
        adapter1 = DatabaseFactory.create_adapter(sqlite_url, echo=True)
        assert adapter1.echo is True
        
        # Test with echo=False
        adapter2 = DatabaseFactory.create_adapter(sqlite_url, echo=False)
        assert adapter2.echo is False
    
    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization"""
        sqlite_url = "sqlite:///test_init.db"
        
        # Initialize manager
        manager = DatabaseManager(sqlite_url, echo=False)
        
        # Verify adapter is initialized
        assert manager.adapter is not None
        assert manager.adapter.database_url == sqlite_url
        assert manager.adapter.echo is False
        
        # Clean up
        if os.path.exists("test_init.db"):
            os.remove("test_init.db")
        
        manager.reset()
    
    def test_database_manager_uninitialized_access(self):
        """Test accessing DatabaseManager without initialization"""
        # Create manager without parameters
        manager = DatabaseManager()
        
        # Should raise error when accessing adapter
        with pytest.raises(RuntimeError) as exc_info:
            _ = manager.adapter
        
        assert "Database not initialized" in str(exc_info.value)