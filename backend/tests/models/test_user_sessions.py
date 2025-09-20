"""
Test suite for UserSessions model
"""
import pytest
from datetime import datetime, UTC, timedelta
from uuid import uuid4
from sqlmodel import SQLModel, Session

from models.user_sessions import UserSessions
from models.user import User


class TestUserSessionModel:
    """Test cases for UserSession model"""
    
    def test_session_creation(self, db_session: Session):
        """Test creating a session"""
        # First create a user
        user_id = str(uuid4())
        user = User(id=user_id, username="session_test_user")
        db_session.add(user)
        db_session.commit()
        
        # Create session
        session = UserSessions(
            username="session_test_user",  # Use the username from the created user
            session_id=UserSessions.generate_session_key(),
            oauth_token="test_token_123"
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.session_id is not None
        assert len(session.session_id) == 32  # UUID without dashes
        assert session.oauth_token == "test_token_123"
    
    def test_session_key_generation(self):
        """Test session key generation"""
        key1 = UserSessions.generate_session_key()
        key2 = UserSessions.generate_session_key()
        
        assert key1 != key2  # Should be unique
        assert len(key1) == 32
        assert len(key2) == 32
        assert "-" not in key1  # No dashes
        assert "-" not in key2
    
    def test_session_expiration(self):
        """Test session expiration checking"""
        session = UserSessions(
            user_id=str(uuid4()),
            session_id=UserSessions.generate_session_key(),
            oauth_token="token"
        )
        
        # New session should not be expired
        assert session.is_expired(3600) is False
        
        # Manually set old accessed_at
        session.accessed_at = datetime.now(UTC) - timedelta(hours=2)
        
        # Should be expired for 1 hour TTL
        assert session.is_expired(3600) is True
        
        # Should not be expired for 3 hour TTL
        assert session.is_expired(10800) is False