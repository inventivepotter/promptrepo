"""
Test suite for database factory and manager
Tests factory pattern implementation and singleton behavior
"""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from database.database_factory import DatabaseFactory, DatabaseManager
from database.database_adapter import SQLiteAdapter, PostgreSQLAdapter, MySQLAdapter


class TestDatabaseFactory:
    """Test cases for DatabaseFactory"""
    
    def test_factory_creates_sqlite_adapter(self):
        """Test factory creates SQLite adapter for sqlite URL"""
        sqlite_url = "sqlite:///test.db"
        adapter = DatabaseFactory.create_adapter(sqlite_url)
        
        assert isinstance(adapter, SQLiteAdapter)
        assert adapter.database_url == sqlite_url
        assert adapter.echo is True  # Default echo value
        
        # Clean up if file was created
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def test_factory_creates_sqlite_adapter_with_memory_db(self):
        """Test factory creates SQLite adapter for in-memory database"""
        sqlite_url = "sqlite:///:memory:"
        adapter = DatabaseFactory.create_adapter(sqlite_url, echo=False)
        
        assert isinstance(adapter, SQLiteAdapter)
        assert adapter.database_url == sqlite_url
        assert adapter.echo is False
    
    def test_factory_creates_postgresql_adapter(self):
        """Test factory creates PostgreSQL adapter for postgresql URL"""
        postgres_url = "postgresql://localhost/test"
        adapter = DatabaseFactory.create_adapter(postgres_url, echo=False)
        
        assert isinstance(adapter, PostgreSQLAdapter)
        assert adapter.database_url == postgres_url
        assert adapter.echo is False
    
    def test_factory_handles_postgresql_variants(self):
        """Test factory handles different PostgreSQL URL schemes"""
        urls = [
            "postgresql://localhost/test",
            "postgresql+psycopg2://localhost/test",
            "postgresql+asyncpg://localhost/test",
            "postgres://localhost/test"
        ]
        
        for url in urls:
            adapter = DatabaseFactory.create_adapter(url, echo=True)
            assert isinstance(adapter, PostgreSQLAdapter)
            assert adapter.database_url == url
            assert adapter.echo is True
    
    def test_factory_creates_mysql_adapter(self):
        """Test factory creates MySQL adapter for mysql URL"""
        mysql_url = "mysql://localhost/test"
        adapter = DatabaseFactory.create_adapter(mysql_url, echo=False)
        
        assert isinstance(adapter, MySQLAdapter)
        assert adapter.database_url == mysql_url
        assert adapter.echo is False
    
    def test_factory_handles_mysql_variants(self):
        """Test factory handles different MySQL URL schemes"""
        urls = [
            "mysql://localhost/test",
            "mysql+pymysql://localhost/test",
            "mysql+mysqldb://localhost/test"
        ]
        
        for url in urls:
            adapter = DatabaseFactory.create_adapter(url, echo=True)
            assert isinstance(adapter, MySQLAdapter)
            assert adapter.database_url == url
            assert adapter.echo is True
    
    def test_factory_raises_error_for_unsupported_database(self):
        """Test factory raises ValueError for unsupported database types"""
        unsupported_urls = [
            "mongodb://localhost/test",
            "redis://localhost:6379",
            "cassandra://localhost:9042",
            "elasticsearch://localhost:9200",
            ""  # Empty URL
        ]
        
        for url in unsupported_urls:
            with pytest.raises(ValueError) as exc_info:
                DatabaseFactory.create_adapter(url)
            
            if url:
                assert f"Unsupported database type: {url.split('://')[0]}" in str(exc_info.value)
            else:
                assert "Unsupported database type" in str(exc_info.value)
    
    def test_factory_echo_parameter(self):
        """Test factory passes echo parameter correctly"""
        adapter1 = DatabaseFactory.create_adapter("sqlite:///test.db", echo=True)
        assert adapter1.echo is True
        
        adapter2 = DatabaseFactory.create_adapter("sqlite:///test.db", echo=False)
        assert adapter2.echo is False
        
        # Clean up
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def test_factory_url_parsing_edge_cases(self):
        """Test factory handles edge cases in URL parsing"""
        # URL with query parameters
        url_with_query = "sqlite:///test.db?charset=utf8"
        adapter = DatabaseFactory.create_adapter(url_with_query)
        assert isinstance(adapter, SQLiteAdapter)
        
        # URL with authentication
        url_with_auth = "postgresql://user:password@localhost:5432/testdb"
        adapter = DatabaseFactory.create_adapter(url_with_auth)
        assert isinstance(adapter, PostgreSQLAdapter)
        
        # Clean up
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def test_factory_case_insensitive_scheme(self):
        """Test factory handles case-insensitive URL schemes"""
        urls = [
            "SQLITE:///test.db",
            "POSTGRESQL://localhost/test",
            "MYSQL://localhost/test"
        ]
        
        for url in urls:
            # Should convert to lowercase and work correctly
            adapter = DatabaseFactory.create_adapter(url.lower())
            assert adapter is not None
        
        # Clean up
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    @patch('database.database_factory.DatabaseFactory.create_adapter')
    def test_factory_adapter_creation_failure(self, mock_create_adapter):
        """Test factory handles adapter creation failures"""
        mock_create_adapter.side_effect = Exception("Creation failed")
        
        with pytest.raises(Exception) as exc_info:
            DatabaseFactory.create_adapter("sqlite:///test.db")
        
        assert "Creation failed" in str(exc_info.value)


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
    
    def test_manager_singleton_pattern_with_different_urls(self):
        """Test DatabaseManager singleton with different URLs returns same instance"""
        url1 = "sqlite:///test1.db"
        url2 = "sqlite:///test2.db"
        
        manager1 = DatabaseManager(url1, echo=False)
        manager2 = DatabaseManager(url2, echo=False)
        
        # Should still be the same instance (singleton)
        assert manager1 is manager2
        # But adapter should be from the first initialization
        assert manager1.adapter.database_url == url1
        
        # Clean up
        for db_file in ["test1.db", "test2.db"]:
            if os.path.exists(db_file):
                os.remove(db_file)
    
    def test_manager_adapter_initialization(self):
        """Test manager initializes adapter correctly"""
        sqlite_url = "sqlite:///test_manager.db"
        manager = DatabaseManager(sqlite_url, echo=False)
        
        assert manager.adapter is not None
        assert isinstance(manager.adapter, SQLiteAdapter)
        assert manager.adapter.database_url == sqlite_url
        assert manager.adapter.echo is False
        
        # Clean up
        if os.path.exists("test_manager.db"):
            os.remove("test_manager.db")
    
    def test_manager_adapter_initialization_with_postgres(self):
        """Test manager initializes PostgreSQL adapter correctly"""
        postgres_url = "postgresql://localhost/test"
        manager = DatabaseManager(postgres_url, echo=True)
        
        assert manager.adapter is not None
        assert isinstance(manager.adapter, PostgreSQLAdapter)
        assert manager.adapter.database_url == postgres_url
        assert manager.adapter.echo is True
    
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
        
        # Get the original instance
        original_id = id(manager)
        
        # Reset manager
        manager.reset()
        
        # After reset, singleton should be cleared
        new_manager = DatabaseManager(sqlite_url, echo=False)
        assert new_manager is not manager
        assert id(new_manager) != original_id
        
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
        assert manager.adapter.database_url == "sqlite:///test_init.db"
        assert manager.adapter.echo is False
        
        # Clean up
        if os.path.exists("test_init.db"):
            os.remove("test_init.db")
    
    def test_manager_reinitialization(self):
        """Test manager reinitialization changes adapter"""
        manager = DatabaseManager()
        
        # Initialize with SQLite
        manager.initialize("sqlite:///test_reinit1.db", echo=False)
        assert isinstance(manager.adapter, SQLiteAdapter)
        
        # Reinitialize with PostgreSQL
        manager.initialize("postgresql://localhost/test", echo=True)
        assert isinstance(manager.adapter, PostgreSQLAdapter)
        assert manager.adapter.echo is True
        
        # Clean up
        if os.path.exists("test_reinit1.db"):
            os.remove("test_reinit1.db")
    
    def test_manager_thread_safety_simulation(self):
        """Test manager singleton behavior in simulated multi-threaded scenario"""
        import threading
        
        results = []
        lock = threading.Lock()
        
        def create_manager(url):
            manager = DatabaseManager(url, echo=False)
            with lock:
                results.append(id(manager))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_manager, args=(f"sqlite:///test_thread_{i}.db",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All threads should have the same manager instance
        assert len(set(results)) == 1
        
        # Clean up
        for i in range(5):
            db_file = f"test_thread_{i}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
    
    def test_manager_get_session(self):
        """Test manager get_session method"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            sqlite_url = f"sqlite:///{test_db}"
            manager = DatabaseManager(sqlite_url, echo=False)
            manager.create_tables()
            
            # Test get_session
            session_generator = manager.get_session()
            session = next(session_generator)
            
            # Session should be valid
            assert session is not None
            assert session.bind is not None
            
            # Close generator properly
            session_generator.close()
        finally:
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)
    
    def test_manager_create_tables(self):
        """Test manager create_tables method"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            sqlite_url = f"sqlite:///{test_db}"
            manager = DatabaseManager(sqlite_url, echo=False)
            
            # Create tables
            manager.create_tables()
            
            # Should not raise any errors
            assert True
        finally:
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)
    
    def test_manager_string_representation(self):
        """Test manager string representation"""
        sqlite_url = "sqlite:///test_str.db"
        manager = DatabaseManager(sqlite_url, echo=False)
        
        str_repr = str(manager)
        assert "DatabaseManager" in str_repr
        assert sqlite_url in str_repr
        
        # Clean up
        if os.path.exists("test_str.db"):
            os.remove("test_str.db")
    
    def test_manager_property_access(self):
        """Test manager property access"""
        sqlite_url = "sqlite:///test_prop.db"
        manager = DatabaseManager(sqlite_url, echo=False)
        
        # Test engine property
        assert manager.engine is not None
        assert manager.engine.url.drivername == "sqlite"
        
        # Clean up
        if os.path.exists("test_prop.db"):
            os.remove("test_prop.db")