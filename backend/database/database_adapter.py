"""
Database Adapter Interface and Implementations
Following the Strategy Pattern and SOLID principles
"""
from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Optional
from sqlmodel import SQLModel, Session as SQLSession, create_engine
from sqlalchemy.engine import Engine
import os
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters (Interface Segregation Principle).
    Each adapter implements database-specific connection and configuration logic.
    """
    
    def __init__(self, database_url: str, echo: bool = False):
        self.database_url = database_url
        self.echo = echo
        self._engine: Optional[Engine] = None
    
    @abstractmethod
    def create_engine(self) -> Engine:
        """Create and return database engine with appropriate configuration"""
        pass
    
    @abstractmethod
    def get_connection_args(self) -> Dict[str, Any]:
        """Get database-specific connection arguments"""
        pass
    
    @abstractmethod
    def prepare_database(self) -> None:
        """Prepare database (e.g., create files for SQLite, check connection for PostgreSQL)"""
        pass
    
    @property
    def engine(self) -> Engine:
        """Lazy initialization of engine (Single Responsibility Principle)"""
        if self._engine is None:
            self.prepare_database()
            self._engine = self.create_engine()
        return self._engine
    
    def create_tables(self) -> None:
        """Create all database tables"""
        SQLModel.metadata.create_all(self.engine)
    
    def get_session(self) -> Generator[SQLSession, None, None]:
        """Get database session"""
        with SQLSession(self.engine) as session:
            yield session


class SQLiteAdapter(DatabaseAdapter):
    """
    SQLite-specific database adapter implementation.
    Handles SQLite-specific configuration and file management.
    """
    
    def get_connection_args(self) -> Dict[str, Any]:
        """SQLite specific connection arguments"""
        return {"check_same_thread": False}
    
    def prepare_database(self) -> None:
        """Ensure SQLite database file and directory exist"""
        # Extract file path from SQLite URL
        database_path = self.database_url.replace('sqlite:///', '')
        if not database_path:
            database_path = "promptrepo.db"
        
        database_dir = os.path.dirname(database_path)
        
        # Create directory if it doesn't exist
        if database_dir and not os.path.exists(database_dir):
            os.makedirs(database_dir)
            logger.info(f"Created database directory: {database_dir}")
        
        # Create database file if it doesn't exist
        if not os.path.exists(database_path):
            open(database_path, 'a').close()
            logger.info(f"Created SQLite database file: {database_path}")
    
    def create_engine(self) -> Engine:
        """Create SQLite engine with appropriate configuration"""
        return create_engine(
            self.database_url,
            echo=self.echo,
            connect_args=self.get_connection_args()
        )


class PostgreSQLAdapter(DatabaseAdapter):
    """
    PostgreSQL-specific database adapter implementation.
    Handles PostgreSQL-specific configuration and connection pooling.
    """
    
    def get_connection_args(self) -> Dict[str, Any]:
        """PostgreSQL specific connection arguments with connection pooling"""
        return {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,  # Verify connections before using
            "pool_recycle": 3600,   # Recycle connections after 1 hour
        }
    
    def prepare_database(self) -> None:
        """
        PostgreSQL doesn't need file preparation.
        Could be extended to check connection or create database if needed.
        """
        pass
    
    def create_engine(self) -> Engine:
        """Create PostgreSQL engine with appropriate configuration"""
        # For PostgreSQL, we pass pool settings directly to create_engine
        return create_engine(
            self.database_url,
            echo=self.echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )


class MySQLAdapter(DatabaseAdapter):
    """
    MySQL-specific database adapter implementation.
    Can be extended in the future for MySQL support.
    """
    
    def get_connection_args(self) -> Dict[str, Any]:
        """MySQL specific connection arguments"""
        return {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    
    def prepare_database(self) -> None:
        """MySQL preparation logic"""
        pass
    
    def create_engine(self) -> Engine:
        """Create MySQL engine with appropriate configuration"""
        return create_engine(
            self.database_url,
            echo=self.echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )