"""
Unit tests for SessionService.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, UTC, timedelta
from sqlmodel import Session

from services.auth.session_service import SessionService
from database.models.user_sessions import UserSessions
from database.models.user import User


class TestSessionService:
    """Test cases for SessionService"""

    def test_init(self):
        """Test SessionService initialization"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        assert service.db == db_session

    def test_is_session_valid_with_valid_session(self):
        """Test is_session_valid with valid session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock valid session
        mock_session = Mock()
        mock_session.accessed_at = datetime.now(UTC) + timedelta(hours=1)
        
        # Mock the exec method chain properly
        mock_exec = Mock()
        mock_exec.first.return_value = mock_session
        db_session.exec.return_value = mock_exec
        
        result = service.is_session_valid("valid_session_id")
        
        # is_session_valid returns the session object if valid, None if invalid
        assert result is not None
        assert result.accessed_at > datetime.now(UTC) - timedelta(minutes=1439)  # Within 24h TTL

    def test_is_session_valid_with_expired_session(self):
        """Test is_session_valid with expired session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock expired session
        mock_session = Mock()
        mock_session.accessed_at = datetime.now(UTC) - timedelta(hours=25)  # More than 24h ago
        
        # Mock the exec method chain properly
        mock_exec = Mock()
        mock_exec.first.return_value = mock_session
        db_session.exec.return_value = mock_exec
        
        result = service.is_session_valid("expired_session_id")
        
        # is_session_valid returns None for expired sessions
        assert result is None

    def test_is_session_valid_with_nonexistent_session(self):
        """Test is_session_valid with non-existent session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock the exec method chain properly
        mock_exec = Mock()
        mock_exec.first.return_value = None
        db_session.exec.return_value = mock_exec
        
        result = service.is_session_valid("nonexistent_session_id")
        
        # is_session_valid returns None for non-existent sessions
        assert result is None

    def test_get_session_by_id_success(self):
        """Test get_session_by_id with existing session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock session with user relationship
        mock_user = Mock(spec=User)
        mock_user.id = "user_123"
        mock_user.username = "testuser"
        
        mock_session = Mock(spec=UserSessions)
        mock_session.id = "session_123"
        mock_session.user_id = "user_123"
        mock_session.user = mock_user
        mock_session.expires_at = datetime.now(UTC) + timedelta(hours=1)
        
        db_session.get.return_value = mock_session
        
        # Mock the exec method chain
        mock_exec = Mock()
        mock_exec.first.return_value = mock_session
        db_session.exec.return_value = mock_exec
        
        result = service.get_session_by_id("session_123")
        
        assert result == mock_session
        db_session.exec.assert_called_once()

    def test_get_session_by_id_not_found(self):
        """Test get_session_by_id with non-existent session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock the exec method chain to return None
        mock_exec = Mock()
        mock_exec.first.return_value = None
        db_session.exec.return_value = mock_exec
        
        result = service.get_session_by_id("nonexistent_session_id")
        
        assert result is None

    def test_create_session(self):
        """Test creating a new session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        user_id = "user_123"
        oauth_token = "oauth_token_123"
        session_data = '{"test": "data"}'
        
        with patch('services.auth.session_service.UserSessions') as mock_sessions_class:
            mock_session = Mock()
            mock_session.session_id = "new_session_id"
            mock_sessions_class.return_value = mock_session
            mock_sessions_class.generate_session_key.return_value = "generated_session_key"
            
            result = service.create_session(
                user_id=user_id,
                oauth_token=oauth_token,
                session_data=session_data
            )
            
            assert result == mock_session
            db_session.add.assert_called_once_with(mock_session)
            db_session.commit.assert_called_once()
            db_session.refresh.assert_called_once_with(mock_session)

    def test_delete_session_success(self):
        """Test deleting an existing session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        mock_session = Mock(spec=UserSessions)
        mock_session.session_id = "session_123"
        
        # Mock the exec method chain
        mock_exec = Mock()
        mock_exec.first.return_value = mock_session
        db_session.exec.return_value = mock_exec
        
        result = service.delete_session("session_123")
        
        assert result is True
        db_session.delete.assert_called_once_with(mock_session)
        db_session.commit.assert_called_once()

    def test_delete_session_not_found(self):
        """Test deleting a non-existent session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock the exec method chain to return None
        mock_exec = Mock()
        mock_exec.first.return_value = None
        db_session.exec.return_value = mock_exec
        
        result = service.delete_session("nonexistent_session_id")
        
        assert result is False
        db_session.delete.assert_not_called()
        db_session.commit.assert_not_called()

    def test_cleanup_expired_sessions(self):
        """Test cleaning up expired sessions"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock the exec method to return expired sessions list
        mock_exec = Mock()
        mock_expired_sessions = [Mock(), Mock(), Mock()]  # 3 expired sessions
        mock_exec.all.return_value = mock_expired_sessions
        db_session.exec.return_value = mock_exec
        
        result = service.cleanup_expired_sessions(ttl_minutes=60)
        
        assert result == 3

    def test_update_session(self):
        """Test updating session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        mock_session = Mock(spec=UserSessions)
        mock_session.session_id = "session_123"
        
        # Mock the exec method chain
        mock_exec = Mock()
        mock_exec.first.return_value = mock_session
        db_session.exec.return_value = mock_exec
        
        new_oauth_token = "new_oauth_token"
        session_data = '{"updated": "data"}'
        
        result = service.update_session(
            session_id="session_123",
            oauth_token=new_oauth_token,
            session_data=session_data
        )
        
        assert result is True
        assert mock_session.oauth_token == new_oauth_token
        assert mock_session.data == session_data
        db_session.add.assert_called_once_with(mock_session)
        db_session.commit.assert_called_once()

    def test_update_session_not_found(self):
        """Test updating non-existent session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        # Mock the exec method chain to return None
        mock_exec = Mock()
        mock_exec.first.return_value = None
        db_session.exec.return_value = mock_exec
        
        result = service.update_session(
            session_id="nonexistent_session_id",
            oauth_token="new_token"
        )
        
        assert result is False
        db_session.add.assert_not_called()
        db_session.commit.assert_not_called()

    def test_get_user_from_session(self):
        """Test getting user from session"""
        db_session = Mock(spec=Session)
        service = SessionService(db_session)
        
        mock_user = Mock(spec=User)
        mock_user.id = "user_123"
        
        mock_session = Mock(spec=UserSessions)
        mock_session.user = mock_user
        
        # Mock the exec method chain
        mock_exec = Mock()
        mock_exec.first.return_value = mock_session
        db_session.exec.return_value = mock_exec
        
        result = service.get_user_from_session("session_123")
        
        assert result == mock_user