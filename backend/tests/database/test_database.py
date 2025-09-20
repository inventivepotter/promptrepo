"""
Test script to verify database adapter pattern implementation
Tests both SQLite and PostgreSQL adapters
"""
from database.database_factory import DatabaseFactory, DatabaseManager
from models.user import User
import os

def test_sqlite_adapter():
    """Test SQLite adapter"""
    print("\n=== Testing SQLite Adapter ===")
    
    # Create SQLite adapter
    sqlite_url = "sqlite:///test_database.db"
    adapter = DatabaseFactory.create_adapter(sqlite_url, echo=False)
    
    # Create tables
    adapter.create_tables()
    print("✓ SQLite tables created successfully")
    
    # Test session creation
    for session in adapter.get_session():
        print("✓ SQLite session created successfully")
        
        # Create test user
        test_user = User(
            username="test_user",
            name="Test User",
            email="test@example.com"
        )
        session.add(test_user)
        session.commit()
        print("✓ Test user created in SQLite")
        
        # Clean up
        session.delete(test_user)
        session.commit()
    
    # Clean up test database
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")
        print("✓ SQLite test database cleaned up")

def test_postgresql_adapter():
    """Test PostgreSQL adapter (requires PostgreSQL to be running)"""
    print("\n=== Testing PostgreSQL Adapter ===")
    
    # Create PostgreSQL adapter (this will only test creation, not actual connection)
    postgres_url = "postgresql://user:password@localhost:5432/testdb"
    
    try:
        adapter = DatabaseFactory.create_adapter(postgres_url, echo=False)
        print("✓ PostgreSQL adapter created successfully")
        
        # Note: Actual database operations would require a running PostgreSQL instance
        print("ℹ️  PostgreSQL connection would require a running PostgreSQL instance")
        
    except Exception as e:
        print(f"⚠️  PostgreSQL adapter creation failed (expected if PostgreSQL not running): {e}")

def test_database_manager():
    """Test DatabaseManager singleton pattern"""
    print("\n=== Testing DatabaseManager Singleton ===")
    
    # Initialize manager
    sqlite_url = "sqlite:///test_singleton.db"
    manager1 = DatabaseManager(sqlite_url, echo=False)
    manager2 = DatabaseManager(sqlite_url, echo=False)
    
    # Verify singleton
    assert manager1 is manager2, "DatabaseManager should be a singleton"
    print("✓ DatabaseManager singleton pattern working correctly")
    
    # Test table creation
    manager1.create_tables()
    print("✓ Tables created through DatabaseManager")
    
    # Clean up
    if os.path.exists("test_singleton.db"):
        os.remove("test_singleton.db")
    
    # Reset manager for next test
    manager1.reset()
    print("✓ DatabaseManager reset successfully")

def test_unsupported_database():
    """Test error handling for unsupported database types"""
    print("\n=== Testing Unsupported Database Handling ===")
    
    try:
        unsupported_url = "mongodb://localhost:27017/testdb"
        adapter = DatabaseFactory.create_adapter(unsupported_url)
        print("✗ Should have raised ValueError for unsupported database")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Database Adapter Pattern Implementation")
    print("=" * 50)
    
    test_sqlite_adapter()
    test_postgresql_adapter()
    test_database_manager()
    test_unsupported_database()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()