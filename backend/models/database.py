from sqlmodel import SQLModel, create_engine, Session as SQLSession
from sqlalchemy.engine import Engine
from typing import Generator
from ..settings.base_settings import settings

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