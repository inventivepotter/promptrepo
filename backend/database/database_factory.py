"""
Database Factory for creating appropriate database adapters
Following the Factory Pattern and Open/Closed Principle
"""
from typing import Optional
from urllib.parse import urlparse
from .database_adapter import (
    DatabaseAdapter,
    SQLiteAdapter,
    PostgreSQLAdapter,
    MySQLAdapter
)


class DatabaseFactory:
    """
    Factory class for creating database adapters based on the database URL.
    Open/Closed Principle: Open for extension (new database types), closed for modification.
    """
    
    @staticmethod
    def create_adapter(database_url: str, echo: bool = False) -> DatabaseAdapter:
        """
        Create and return appropriate database adapter based on the database URL scheme.
        
        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL statements
            
        Returns:
            DatabaseAdapter: Appropriate adapter instance for the database type
            
        Raises:
            ValueError: If database type is not supported
        """
        parsed_url = urlparse(database_url)
        scheme = parsed_url.scheme.lower()
        
        # Map database schemes to their respective adapters
        adapters_map = {
            'sqlite': SQLiteAdapter,
            'postgresql': PostgreSQLAdapter,
            'postgresql+psycopg2': PostgreSQLAdapter,
            'postgresql+asyncpg': PostgreSQLAdapter,
            'postgres': PostgreSQLAdapter,
            'mysql': MySQLAdapter,
            'mysql+pymysql': MySQLAdapter,
            'mysql+mysqldb': MySQLAdapter,
        }
        
        # Get the appropriate adapter class
        adapter_class = adapters_map.get(scheme)
        
        if adapter_class is None:
            supported = ', '.join(adapters_map.keys())
            raise ValueError(
                f"Unsupported database type: {scheme}. "
                f"Supported types are: {supported}"
            )
        
        # Create and return the adapter instance
        adapter = adapter_class(database_url, echo)
        print(f"Created {adapter_class.__name__} for database: {scheme}")
        
        return adapter


class DatabaseManager:
    """
    Singleton manager for database operations.
    Ensures single database adapter instance throughout the application.
    """
    _instance: Optional['DatabaseManager'] = None
    _adapter: Optional[DatabaseAdapter] = None
    
    def __new__(cls, database_url: Optional[str] = None, echo: bool = False):
        """
        Singleton pattern implementation.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        """
        Initialize the database manager with an adapter.
        Only initializes on first creation due to singleton pattern.
        """
        if self._adapter is None and database_url:
            self._adapter = DatabaseFactory.create_adapter(database_url, echo)
    
    @property
    def adapter(self) -> DatabaseAdapter:
        """Get the database adapter instance."""
        if self._adapter is None:
            raise RuntimeError(
                "Database not initialized. "
                "Call DatabaseManager with database_url first."
            )
        return self._adapter
    
    def initialize(self, database_url: str, echo: bool = False) -> None:
        """
        Initialize or reinitialize the database adapter.
        Useful for changing database configuration at runtime.
        """
        self._adapter = DatabaseFactory.create_adapter(database_url, echo)
    
    def create_tables(self) -> None:
        """Create all database tables."""
        self.adapter.create_tables()
    
    def get_session(self):
        """Get database session."""
        return self.adapter.get_session()
    
    @property
    def engine(self):
        """Get database engine."""
        return self.adapter.engine
    
    def reset(self) -> None:
        """
        Reset the database manager.
        Useful for testing or switching databases.
        """
        self._adapter = None
        DatabaseManager._instance = None