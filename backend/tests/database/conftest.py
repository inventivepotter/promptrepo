"""
Configuration for database tests.
This extends the root conftest with database-specific fixtures.
"""
import pytest
from sqlmodel import SQLModel, Session

# Import all models to ensure they are registered in the metadata
from backend.models.user import User
from backend.models.user_sessions import UserSessions
from backend.models.user_repos import UserRepos
from backend.models.user_llm_configs import UserLLMConfigs

# This will inherit the db_session fixture from the root conftest
# No need to redefine it here unless we need database-specific behavior