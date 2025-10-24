"""
Tests for OAuth state manager.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from typing import Optional

from services.oauth.state_manager import StateManager
from services.oauth.models import InvalidStateError
from schemas.oauth_provider_enum import OAuthProvider


class TestStateManager:
    """Test cases for StateManager class."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    def test_init(self, mock_db):
        """Test StateManager initialization."""
        state_manager = StateManager(db=mock_db)
        
        assert state_manager.state_expiry_minutes == 10
        
        # Test with custom expiry
        custom_manager = StateManager(db=mock_db, state_expiry_minutes=5)
        assert custom_manager.state_expiry_minutes == 5

    def test_generate_state(self, mock_db):
        """Test state generation."""
        state_manager = StateManager(db=mock_db)
        
        # Test with default length (32 bytes = ~43 chars in base64)
        state = state_manager.generate_state()
        assert isinstance(state, str)
        assert len(state) > 0  # Just ensure it's not empty
        assert len(state) >= 32  # Should be at least 32 chars
        
        # Test with custom length (16 bytes = ~22 chars in base64)
        custom_length_state = state_manager.generate_state(length=16)
        assert len(custom_length_state) > 0
        assert len(custom_length_state) >= 16  # Should be at least 16 chars

    def test_store_state(self, mock_db, sample_oauth_state):
        """Test storing a state."""
        state_manager = StateManager(db=mock_db)
        
        # Mock the DAO save method
        state_manager.oauth_state_dao.save_state = Mock()
        
        # Store a valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=OAuthProvider.GITHUB,  # Use enum instead of sample_oauth_state.provider
            redirect_uri=sample_oauth_state.redirect_uri,
            scopes=sample_oauth_state.scopes,
            metadata=sample_oauth_state.metadata
        )
        
        # Verify state was stored by checking DAO was called
        assert state_manager.oauth_state_dao.save_state.called

    def test_store_state_validation(self, mock_db):
        """Test state validation when storing."""
        state_manager = StateManager(db=mock_db)
        
        # Test with empty state
        with pytest.raises(ValueError, match="State must be a non-empty string"):
            state_manager.store_state(
                state="",
                provider=OAuthProvider.GITHUB,
                redirect_uri="https://example.com/callback"
            )
        
        # Test with None state
        with pytest.raises(ValueError, match="State must be a non-empty string"):
            state_manager.store_state(
                state=None,  # type: ignore
                provider=OAuthProvider.GITHUB,
                redirect_uri="https://example.com/callback"
            )
        
        # Test with None provider
        with pytest.raises(ValueError, match="Provider must be a valid OAuthProvider enum"):
            state_manager.store_state(
                state="test_state",
                provider=None,  # type: ignore
                redirect_uri="https://example.com/callback"
            )
        
        # Test with empty redirect URI
        with pytest.raises(ValueError, match="Redirect URI must be a non-empty string"):
            state_manager.store_state(
                state="test_state",
                provider=OAuthProvider.GITHUB,
                redirect_uri=""
            )

    def test_validate_state(self, mock_db):
        """Test state validation."""
        state_manager = StateManager(db=mock_db)
        
        # Mock valid state from DAO
        from database.models import OAuthState as DBOAuthState
        mock_state = Mock(spec=DBOAuthState)
        mock_state.provider = OAuthProvider.GITHUB
        mock_state.is_expired = False
        
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=mock_state)
        state_manager.oauth_state_dao.delete_state_by_token = Mock()
        
        # Test valid state
        assert state_manager.validate_state("test_state", OAuthProvider.GITHUB) is True
        
        # Test with wrong provider
        assert state_manager.validate_state("test_state", OAuthProvider.GITLAB) is False
        
        # Test non-existent state
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=None)
        assert state_manager.validate_state("non_existent_state", OAuthProvider.GITHUB) is False

    def test_get_state_metadata(self, mock_db):
        """Test getting state metadata."""
        state_manager = StateManager(db=mock_db)
        
        # Mock valid state with metadata
        from database.models import OAuthState as DBOAuthState
        mock_state = Mock(spec=DBOAuthState)
        mock_state.meta_data = {"user_id": "12345"}
        mock_state.is_expired = False
        
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=mock_state)
        
        # Test getting metadata
        metadata = state_manager.get_state_metadata("test_state")
        assert metadata == {"user_id": "12345"}
        
        # Test with non-existent state
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=None)
        with pytest.raises(InvalidStateError, match="State not found"):
            state_manager.get_state_metadata("non_existent_state")

    def test_get_state_metadata_expired(self, mock_db):
        """Test getting metadata for expired state."""
        state_manager = StateManager(db=mock_db)
        
        # Mock expired state
        from database.models import OAuthState as DBOAuthState
        mock_state = Mock(spec=DBOAuthState)
        mock_state.is_expired = True
        
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=mock_state)
        state_manager.oauth_state_dao.delete_state_by_token = Mock()
        
        # Test getting metadata for expired state
        with pytest.raises(InvalidStateError, match="State expired"):
            state_manager.get_state_metadata("expired_state")
        
        # Verify delete was called
        assert state_manager.oauth_state_dao.delete_state_by_token.called

    def test_get_state_data(self, mock_db):
        """Test getting complete state data."""
        state_manager = StateManager(db=mock_db)
        
        # Mock valid state
        from database.models import OAuthState as DBOAuthState
        mock_state = Mock(spec=DBOAuthState)
        mock_state.is_expired = False
        
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=mock_state)
        
        # Test getting valid state data
        state_data = state_manager.get_state_data("test_state")
        assert state_data is not None
        
        # Test getting non-existent state data
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=None)
        non_existent_data = state_manager.get_state_data("non_existent_state")
        assert non_existent_data is None

    def test_remove_state(self, mock_db):
        """Test removing a state."""
        state_manager = StateManager(db=mock_db)
        
        # Mock successful removal
        state_manager.oauth_state_dao.delete_state_by_token = Mock(return_value=True)
        
        # Remove state
        result = state_manager.remove_state("test_state")
        assert result is True
        
        # Try to remove non-existent state
        state_manager.oauth_state_dao.delete_state_by_token = Mock(return_value=False)
        result = state_manager.remove_state("non_existent_state")
        assert result is False

    def test_cleanup_expired_states(self, mock_db):
        """Test cleaning up expired states."""
        state_manager = StateManager(db=mock_db)
        
        # Mock cleanup returning 1 removed state
        state_manager.oauth_state_dao.cleanup_expired_states = Mock(return_value=1)
        
        # Clean up expired states
        removed_count = state_manager.cleanup_expired_states()
        assert removed_count == 1

    # Removed test_get_all_states as method doesn't exist in current StateManager

    # Removed test_clear_all_states as method doesn't exist in current StateManager

    # Removed test_len as __len__ method doesn't exist in current StateManager

    def test_contains(self, mock_db):
        """Test __contains__ method."""
        state_manager = StateManager(db=mock_db)
        
        # Mock valid state
        from database.models import OAuthState as DBOAuthState
        mock_state = Mock(spec=DBOAuthState)
        mock_state.is_expired = False
        
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=mock_state)
        
        # Test contains
        assert "test_state" in state_manager
        
        # Test non-existent state
        state_manager.oauth_state_dao.get_state_by_token = Mock(return_value=None)
        assert "non_existent_state" not in state_manager

    # Removed test_is_expired_with_mock as it tests OAuthState model, not StateManager