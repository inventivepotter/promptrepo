"""
Tests for OAuth state manager.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from typing import Optional

from services.oauth.state_manager import StateManager
from services.oauth.models import OAuthState, InvalidStateError


class TestStateManager:
    """Test cases for StateManager class."""

    def test_init(self):
        """Test StateManager initialization."""
        state_manager = StateManager()
        
        assert state_manager.state_expiry_minutes == 10
        assert state_manager._states == {}
        
        # Test with custom expiry
        custom_manager = StateManager(state_expiry_minutes=5)
        assert custom_manager.state_expiry_minutes == 5

    def test_generate_state(self):
        """Test state generation."""
        state_manager = StateManager()
        
        # Test with default length (32 bytes = ~43 chars in base64)
        state = state_manager.generate_state()
        assert isinstance(state, str)
        assert len(state) > 0  # Just ensure it's not empty
        assert len(state) >= 32  # Should be at least 32 chars
        
        # Test with custom length (16 bytes = ~22 chars in base64)
        custom_length_state = state_manager.generate_state(length=16)
        assert len(custom_length_state) > 0
        assert len(custom_length_state) >= 16  # Should be at least 16 chars

    def test_store_state(self, sample_oauth_state):
        """Test storing a state."""
        state_manager = StateManager()
        
        # Store a valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri,
            scopes=sample_oauth_state.scopes,
            metadata=sample_oauth_state.metadata
        )
        
        # Verify state was stored
        assert sample_oauth_state.state in state_manager._states
        stored_state = state_manager._states[sample_oauth_state.state]
        assert stored_state.state == sample_oauth_state.state
        assert stored_state.provider == sample_oauth_state.provider
        assert stored_state.redirect_uri == sample_oauth_state.redirect_uri
        assert stored_state.scopes == sample_oauth_state.scopes
        assert stored_state.metadata == sample_oauth_state.metadata

    def test_store_state_validation(self):
        """Test state validation when storing."""
        state_manager = StateManager()
        
        # Test with empty state
        with pytest.raises(ValueError, match="State must be a non-empty string"):
            state_manager.store_state(
                state="",
                provider="github",
                redirect_uri="https://example.com/callback"
            )
        
        # Test with None state
        with pytest.raises(ValueError, match="State must be a non-empty string"):
            state_manager.store_state(
                state=None,  # type: ignore
                provider="github",
                redirect_uri="https://example.com/callback"
            )
        
        # Test with empty provider
        with pytest.raises(ValueError, match="Provider must be a non-empty string"):
            state_manager.store_state(
                state="test_state",
                provider="",
                redirect_uri="https://example.com/callback"
            )
        
        # Test with empty redirect URI
        with pytest.raises(ValueError, match="Redirect URI must be a non-empty string"):
            state_manager.store_state(
                state="test_state",
                provider="github",
                redirect_uri=""
            )

    def test_validate_state(self, sample_oauth_state, expired_oauth_state):
        """Test state validation."""
        state_manager = StateManager()
        
        # Store valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Test valid state
        assert state_manager.validate_state(sample_oauth_state.state, "github") is True
        
        # Test with wrong provider (case-insensitive)
        assert state_manager.validate_state(sample_oauth_state.state, "GITHUB") is True
        assert state_manager.validate_state(sample_oauth_state.state, "gitlab") is False
        
        # Test non-existent state
        assert state_manager.validate_state("non_existent_state", "github") is False
        
        # Test expired state (should be removed)
        assert state_manager.validate_state(expired_oauth_state.state, "github") is False
        assert expired_oauth_state.state not in state_manager._states

    def test_get_state_metadata(self, sample_oauth_state):
        """Test getting state metadata."""
        state_manager = StateManager()
        
        # Store state with metadata
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri,
            metadata=sample_oauth_state.metadata
        )
        
        # Test getting metadata
        metadata = state_manager.get_state_metadata(sample_oauth_state.state)
        assert metadata == sample_oauth_state.metadata
        
        # Test with non-existent state
        with pytest.raises(InvalidStateError, match="State not found"):
            state_manager.get_state_metadata("non_existent_state")

    def test_get_state_metadata_expired(self, expired_oauth_state):
        """Test getting metadata for expired state."""
        state_manager = StateManager()
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Test getting metadata for expired state
        with pytest.raises(InvalidStateError, match="State expired"):
            state_manager.get_state_metadata(expired_oauth_state.state)
        
        # Verify expired state was removed
        assert expired_oauth_state.state not in state_manager._states

    def test_get_state_data(self, sample_oauth_state, expired_oauth_state):
        """Test getting complete state data."""
        state_manager = StateManager()
        
        # Store valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri,
            scopes=sample_oauth_state.scopes,
            metadata=sample_oauth_state.metadata
        )
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Test getting valid state data
        state_data = state_manager.get_state_data(sample_oauth_state.state)
        assert state_data is not None
        assert state_data.state == sample_oauth_state.state
        assert state_data.provider == sample_oauth_state.provider
        assert state_data.redirect_uri == sample_oauth_state.redirect_uri
        assert state_data.scopes == sample_oauth_state.scopes
        assert state_data.metadata == sample_oauth_state.metadata
        
        # Test getting non-existent state data
        non_existent_data = state_manager.get_state_data("non_existent_state")
        assert non_existent_data is None
        
        # Test getting expired state data (should be removed)
        expired_data = state_manager.get_state_data(expired_oauth_state.state)
        assert expired_data is None
        assert expired_oauth_state.state not in state_manager._states

    def test_remove_state(self, sample_oauth_state):
        """Test removing a state."""
        state_manager = StateManager()
        
        # Store state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Verify state exists
        assert sample_oauth_state.state in state_manager._states
        
        # Remove state
        result = state_manager.remove_state(sample_oauth_state.state)
        assert result is True
        assert sample_oauth_state.state not in state_manager._states
        
        # Try to remove non-existent state
        result = state_manager.remove_state("non_existent_state")
        assert result is False

    def test_cleanup_expired_states(self, sample_oauth_state, expired_oauth_state):
        """Test cleaning up expired states."""
        state_manager = StateManager()
        
        # Store valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Verify both states exist
        assert len(state_manager._states) == 2
        
        # Clean up expired states
        removed_count = state_manager.cleanup_expired_states()
        assert removed_count == 1
        assert sample_oauth_state.state in state_manager._states
        assert expired_oauth_state.state not in state_manager._states

    def test_get_all_states(self, sample_oauth_state, expired_oauth_state):
        """Test getting all states."""
        state_manager = StateManager()
        
        # Store valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Get all states (should clean up expired states)
        all_states = state_manager.get_all_states()
        
        # Verify only valid state is returned
        assert len(all_states) == 1
        assert sample_oauth_state.state in all_states
        assert expired_oauth_state.state not in all_states
        
        # Verify expired state was removed from storage
        assert expired_oauth_state.state not in state_manager._states

    def test_clear_all_states(self, sample_oauth_state, expired_oauth_state):
        """Test clearing all states."""
        state_manager = StateManager()
        
        # Store valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        
        # Verify states exist
        assert len(state_manager._states) == 2
        
        # Clear all states
        cleared_count = state_manager.clear_all_states()
        assert cleared_count == 2
        assert len(state_manager._states) == 0

    def test_len(self, sample_oauth_state, expired_oauth_state):
        """Test __len__ method."""
        state_manager = StateManager()
        
        # Initially empty
        assert len(state_manager) == 0
        
        # Store valid state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        assert len(state_manager) == 1
        
        # Store expired state (manually set created_at)
        state_manager._states[expired_oauth_state.state] = expired_oauth_state
        assert len(state_manager) == 2

    def test_contains(self, sample_oauth_state):
        """Test __contains__ method."""
        state_manager = StateManager()
        
        # Store state
        state_manager.store_state(
            state=sample_oauth_state.state,
            provider=sample_oauth_state.provider,
            redirect_uri=sample_oauth_state.redirect_uri
        )
        
        # Test contains
        assert sample_oauth_state.state in state_manager
        assert "non_existent_state" not in state_manager

    @patch('services.oauth.models.datetime')
    def test_is_expired_with_mock(self, mock_datetime, sample_oauth_state):
        """Test is_expired property with mocked datetime."""
        from datetime import timezone
        # Set up mock datetime
        fixed_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now
        
        # Create state that will expire in 5 minutes
        created_at = fixed_now - timedelta(minutes=5)
        state = OAuthState(
            state="test_state",
            provider="github",
            redirect_uri="https://example.com/callback",
            created_at=created_at
        )
        
        # State should not be expired (default expiry is 10 minutes)
        assert state.is_expired is False
        
        # Create state that expired 5 minutes ago
        expired_created_at = fixed_now - timedelta(minutes=15)
        expired_state = OAuthState(
            state="expired_state",
            provider="github",
            redirect_uri="https://example.com/callback",
            created_at=expired_created_at
        )
        
        # State should be expired
        assert expired_state.is_expired is True