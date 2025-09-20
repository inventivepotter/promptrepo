"""
OAuth State Manager

This module handles OAuth state management for CSRF protection.
It generates, stores, validates, and cleans up OAuth states.
"""

import secrets
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from .models import OAuthState, InvalidStateError


class StateManager:
    """
    Manages OAuth state for CSRF protection.
    
    This class handles the generation, storage, validation, and cleanup
    of OAuth states used to prevent CSRF attacks during OAuth flows.
    """
    
    def __init__(self, state_expiry_minutes: int = 10):
        """
        Initialize the state manager.
        
        Args:
            state_expiry_minutes: Minutes after which a state expires
        """
        self.state_expiry_minutes = state_expiry_minutes
        self._states: Dict[str, OAuthState] = {}
    
    def generate_state(self, length: int = 32) -> str:
        """
        Generate a secure random state token.
        
        Args:
            length: Length of the state token (default: 32)
            
        Returns:
            Secure random state token
        """
        return secrets.token_urlsafe(length)
    
    def store_state(
        self, 
        state: str, 
        provider: str, 
        redirect_uri: str,
        scopes: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store OAuth state with associated data.
        
        Args:
            state: State token to store
            provider: OAuth provider name
            redirect_uri: Callback URL
            scopes: List of requested scopes
            metadata: Additional metadata to store
            
        Raises:
            ValueError: If state is empty or invalid
        """
        if not state or not isinstance(state, str):
            raise ValueError("State must be a non-empty string")
        
        if not provider or not isinstance(provider, str):
            raise ValueError("Provider must be a non-empty string")
        
        if not redirect_uri or not isinstance(redirect_uri, str):
            raise ValueError("Redirect URI must be a non-empty string")
        
        # Create OAuth state object
        oauth_state = OAuthState(
            state=state,
            provider=provider.lower(),
            redirect_uri=redirect_uri,
            scopes=scopes or [],
            metadata=metadata or {}
        )
        
        # Store state
        self._states[state] = oauth_state
    
    def validate_state(self, state: str, provider: str) -> bool:
        """
        Validate OAuth state and provider match.
        
        Args:
            state: State token to validate
            provider: OAuth provider name
            
        Returns:
            True if state is valid and matches provider, False otherwise
        """
        if not state or state not in self._states:
            return False
        
        oauth_state = self._states[state]
        
        # Check if state is expired
        if oauth_state.is_expired:
            # Clean up expired state
            del self._states[state]
            return False
        
        # Check provider match (case-insensitive)
        if oauth_state.provider != provider.lower():
            return False
        
        return True
    
    def get_state_metadata(self, state: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata associated with a state.
        
        Args:
            state: State token
            
        Returns:
            Metadata dictionary if state exists and is valid, None otherwise
            
        Raises:
            InvalidStateError: If state is not found or expired
        """
        if state not in self._states:
            raise InvalidStateError(f"State not found: {state}")
        
        oauth_state = self._states[state]
        
        # Check expiration
        if oauth_state.is_expired:
            # Clean up expired state
            del self._states[state]
            raise InvalidStateError(f"State expired: {state}")
        
        return oauth_state.metadata
    
    def get_state_data(self, state: str) -> Optional[OAuthState]:
        """
        Get complete OAuth state data.
        
        Args:
            state: State token
            
        Returns:
            OAuthState object if state exists and is valid, None otherwise
        """
        if state not in self._states:
            return None
        
        oauth_state = self._states[state]
        
        # Check expiration
        if oauth_state.is_expired:
            # Clean up expired state
            del self._states[state]
            return None
        
        return oauth_state
    
    def remove_state(self, state: str) -> bool:
        """
        Remove a stored state.
        
        Args:
            state: State token to remove
            
        Returns:
            True if state was removed, False if not found
        """
        return self._states.pop(state, None) is not None
    
    def cleanup_expired_states(self) -> int:
        """
        Remove all expired states from storage.
        
        Returns:
            Number of expired states removed
        """
        expired_states = []
        
        for state, oauth_state in self._states.items():
            if oauth_state.is_expired:
                expired_states.append(state)
        
        # Remove expired states
        for state in expired_states:
            del self._states[state]
        
        return len(expired_states)
    
    def get_all_states(self) -> Dict[str, OAuthState]:
        """
        Get all currently stored states.
        
        Note: This is primarily for debugging and testing purposes.
        
        Returns:
            Dictionary of state tokens to OAuthState objects
        """
        # First, clean up any expired states
        self.cleanup_expired_states()
        
        # Return a copy to prevent external modification
        return self._states.copy()
    
    def clear_all_states(self) -> int:
        """
        Clear all stored states.
        
        Warning: This is primarily for testing purposes.
        
        Returns:
            Number of states cleared
        """
        count = len(self._states)
        self._states.clear()
        return count
    
    def __len__(self) -> int:
        """Get number of stored states."""
        return len(self._states)
    
    def __contains__(self, state: str) -> bool:
        """Check if state exists in storage."""
        return state in self._states