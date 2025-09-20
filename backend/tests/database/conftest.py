"""
Configuration for database tests.
This extends the root conftest with database-specific fixtures.
"""
import pytest
from sqlmodel import SQLModel, Session

# Models are imported and registered in the root conftest.py's db_engine fixture.
# Importing them here again can cause 'table already defined' errors during pytest's
# collection phase. The db_session fixture from the root conftest is inherited.