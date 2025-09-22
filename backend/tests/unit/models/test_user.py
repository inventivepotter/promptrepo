"""
Test suite for User model
"""
import pytest
from datetime import datetime, UTC
from uuid import uuid4
from sqlmodel import SQLModel, Session

from database.models.user import User


class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self, db_session: Session):
        """Test creating a user"""
        user = User(
            id=str(uuid4()),
            username="testuser",
            name="Test User",
            email="test@example.com",
            oauth_provider="github",
            oauth_user_id=12345,
            avatar_url="https://avatar.url",
            html_url="https://github.com/testuser"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        saved_user = db_session.query(User).filter_by(username="testuser").first()
        assert saved_user is not None
        assert saved_user.username == "testuser"
        assert saved_user.name == "Test User"
        assert saved_user.email == "test@example.com"
        assert saved_user.oauth_user_id == 12345
    
    def test_user_unique_username(self, db_session: Session):
        """Test username uniqueness constraint"""
        user1 = User(id=str(uuid4()), username="unique_user", oauth_provider="github", oauth_user_id=123)
        user2 = User(id=str(uuid4()), username="unique_user", oauth_provider="github", oauth_user_id=456)
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_timestamps(self, db_session: Session):
        """Test user timestamps are set correctly"""
        user = User(id=str(uuid4()), username="timestamp_user", oauth_provider="github", oauth_user_id=789)
        
        db_session.add(user)
        db_session.commit()
        
        assert user.created_at is not None
        assert user.modified_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.modified_at, datetime)