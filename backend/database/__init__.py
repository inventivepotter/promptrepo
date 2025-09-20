"""
Database module initialization
Exports the main database components for easy access
"""
from .database_factory import DatabaseFactory, DatabaseManager
from .database_adapter import (
    DatabaseAdapter,
    SQLiteAdapter,
    PostgreSQLAdapter,
    MySQLAdapter
)

__all__ = [
    'DatabaseFactory',
    'DatabaseManager',
    'DatabaseAdapter',
    'SQLiteAdapter',
    'PostgreSQLAdapter',
    'MySQLAdapter'
]