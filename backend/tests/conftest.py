"""
Root configuration for pytest tests.
Creates a fresh in-memory SQLite database for each test.
"""
import pytest
from sqlmodel import SQLModel, create_engine, Session

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """
    Creates a test database engine for the entire test session.
    
    This fixture is session-scoped, meaning the engine is created only once
    for all tests. The actual database and tables are created and torn down
    for each test function by the db_connection fixture for maximum isolation.
    """
    # Create engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()


@pytest.fixture
def db_connection(db_engine):
    """
    Provides a database connection for each test function.
    
    This fixture is function-scoped, ensuring complete isolation between tests.
    For each test, it:
    1. Creates all tables in the in-memory database. This also triggers
       SQLAlchemy's "autobegin" feature, so the connection is now in a transaction.
    2. Yields the connection, which is already within an active transaction.
    3. In the teardown, it rolls back the transaction (undoing all data changes)
       and drops all tables.
    
    This "create, transact, rollback, drop" cycle ensures that no data
    or schema state persists between tests, which is the most reliable
    way to prevent test interference.
    """
    connection = db_engine.connect()
    # Create all tables. This will also start a transaction ("autobegin").
    SQLModel.metadata.create_all(connection)
    
    try:
        yield connection
    finally:
        # Rollback the transaction that was auto-started by create_all().
        # This undoes any changes made during the test.
        connection.rollback()
        # Drop all tables to ensure a clean schema for the next test function.
        SQLModel.metadata.drop_all(connection)
        connection.close()


@pytest.fixture
def db_session(db_connection):
    """
    Provides a database session for each test.
    
    The session is bound to the function-scoped db_connection. This ensures
    that each test runs with a completely fresh database schema and within
    a transaction that is rolled back after the test, providing maximum
    data isolation.
    """
    # Create a session bound to the test-specific connection
    session = Session(bind=db_connection)
    
    try:
        yield session
    finally:
        # Closing the session. The connection's transaction will be
        # rolled back and tables dropped by the db_connection fixture.
        session.close()