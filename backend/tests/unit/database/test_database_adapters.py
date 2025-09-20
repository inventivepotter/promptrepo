"""
Test suite for database adapters
Tests SQLite, PostgreSQL, and MySQL adapter implementations
"""
import os
from database.database_adapter import SQLiteAdapter, PostgreSQLAdapter, MySQLAdapter
from models.user import User


class TestSQLiteAdapter:
    """Test cases for SQLite adapter"""
    
    def test_sqlite_adapter_creation(self):
        """Test SQLite adapter can be created"""
        sqlite_url = "sqlite:///test_sqlite.db"
        adapter = SQLiteAdapter(sqlite_url, echo=False)
        
        assert adapter is not None
        assert adapter.database_url == sqlite_url
        assert adapter.echo is False
    
    def test_sqlite_connection_args(self):
        """Test SQLite returns correct connection arguments"""
        adapter = SQLiteAdapter("sqlite:///test.db")
        args = adapter.get_connection_args()
        
        assert args == {"check_same_thread": False}
    
    def test_sqlite_database_preparation(self):
        """Test SQLite creates database file"""
        test_db = "test_prep_sqlite.db"
        sqlite_url = f"sqlite:///{test_db}"
        adapter = SQLiteAdapter(sqlite_url, echo=False)
        
        # Prepare database (should create file)
        adapter.prepare_database()
        
        # Check file exists
        assert os.path.exists(test_db)
        
        # Clean up
        os.remove(test_db)
    
    def test_sqlite_table_creation(self):
        """Test SQLite can create tables"""
        test_db = "test_tables.db"
        sqlite_url = f"sqlite:///{test_db}"
        adapter = SQLiteAdapter(sqlite_url, echo=False)
        
        # Create tables
        adapter.create_tables()
        
        # Test session creation
        for session in adapter.get_session():
            # Try to query (tables should exist)
            users = session.query(User).all()
            assert users == []
        
        # Clean up
        os.remove(test_db)


class TestPostgreSQLAdapter:
    """Test cases for PostgreSQL adapter"""
    
    def test_postgresql_adapter_creation(self):
        """Test PostgreSQL adapter can be created"""
        postgres_url = "postgresql://user:pass@localhost:5432/testdb"
        adapter = PostgreSQLAdapter(postgres_url, echo=False)
        
        assert adapter is not None
        assert adapter.database_url == postgres_url
        assert adapter.echo is False
    
    def test_postgresql_connection_args(self):
        """Test PostgreSQL returns correct connection arguments"""
        adapter = PostgreSQLAdapter("postgresql://localhost/test")
        args = adapter.get_connection_args()
        
        assert args["pool_size"] == 10
        assert args["max_overflow"] == 20
        assert args["pool_pre_ping"] is True
        assert args["pool_recycle"] == 3600


class TestMySQLAdapter:
    """Test cases for MySQL adapter"""
    
    def test_mysql_adapter_creation(self):
        """Test MySQL adapter can be created"""
        mysql_url = "mysql://user:pass@localhost:3306/testdb"
        adapter = MySQLAdapter(mysql_url, echo=False)
        
        assert adapter is not None
        assert adapter.database_url == mysql_url
        assert adapter.echo is False
    
    def test_mysql_connection_args(self):
        """Test MySQL returns correct connection arguments"""
        adapter = MySQLAdapter("mysql://localhost/test")
        args = adapter.get_connection_args()
        
        assert args["pool_size"] == 10
        assert args["max_overflow"] == 20
        assert args["pool_pre_ping"] is True
        assert args["pool_recycle"] == 3600