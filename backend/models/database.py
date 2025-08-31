from sqlmodel import SQLModel, create_engine, Session as SQLSession
from sqlalchemy.engine import Engine
from typing import Generator
from settings.base_settings import settings
import os

# Ensure database file exists
# Extract the file path from the database URL (remove sqlite:/// prefix)
database_path = settings.database_url.replace('sqlite:///', '') or "promptrepo.db"
database_dir = os.path.dirname(database_path)

# Create directory if it doesn't exist
if database_dir and not os.path.exists(database_dir):
    os.makedirs(database_dir)
    print(f"Created directory: {database_dir}")

# Create database file if it doesn't exist
if not os.path.exists(database_path):
    # Create empty database file
    open(database_path, 'a').close()
    print(f"Created database file: {database_path}")

# Create engine
engine: Engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[SQLSession, None, None]:
    """Dependency to get database session"""
    with SQLSession(engine) as session:
        yield session