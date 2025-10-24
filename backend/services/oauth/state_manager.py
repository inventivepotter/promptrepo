"""
OAuth State Manager

This module handles OAuth state management for CSRF protection.
It generates, stores, validates, and cleans up OAuth states.
"""

import secrets
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional, Any
from sqlmodel import Session

from database.models import OAuthState as DBOAuthState
from database.daos.oauth_state import OAuthStateDAO
from schemas.oauth_provider_enum import OAuthProvider
from services.oauth.models import InvalidStateError


class StateManager:
    """
    Manages OAuth state for CSRF protection.
    
    This class handles the generation, storage, validation, and cleanup
    of OAuth states used to prevent CSRF attacks during OAuth flows.
    """
    
    def __init__(self, db: Session, state_expiry_minutes: int = 10):
        """
        Initialize the state manager.
        
        Args:
            db: Database session
            state_expiry_minutes: Minutes after which a state expires
        """
        self.oauth_state_dao = OAuthStateDAO(db=db)
        self.state_expiry_minutes = state_expiry_minutes
    
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
        provider: OAuthProvider,
        redirect_uri: str,
        scopes: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        promptrepo_redirect_url: Optional[str] = None
    ) -> None:
        """
        Store OAuth state with associated data.
        
        Args:
            state: State token to store
            provider: OAuth provider name
            redirect_uri: Callback URL
            scopes: List of requested scopes
            metadata: Additional metadata to store
            promptrepo_redirect_url: PromptRepo app redirect URL after login
            
        Raises:
            ValueError: If state is empty or invalid
        """
        if not state or not isinstance(state, str):
            raise ValueError("State must be a non-empty string")
        
        if not provider or not isinstance(provider, OAuthProvider):
            raise ValueError("Provider must be a valid OAuthProvider enum")
        
        if not redirect_uri or not isinstance(redirect_uri, str):
            raise ValueError("Redirect URI must be a non-empty string")
        
        # Prepare metadata
        final_metadata = metadata or {}
        if promptrepo_redirect_url:
            final_metadata["promptrepo_redirect_url"] = promptrepo_redirect_url
        
        # Create OAuth state object for database
        expires_at = datetime.now(UTC) + timedelta(minutes=self.state_expiry_minutes)
        db_oauth_state = DBOAuthState(
            state_token=state,
            provider=provider,
            redirect_uri=redirect_uri,
            scopes=",".join(scopes or []),
            meta_data=final_metadata,
            expires_at=expires_at
        )
        
        # Store state in database
        self.oauth_state_dao.save_state(db_oauth_state)
    
    def validate_state(self, state: str, provider: str) -> bool:
        """
        Validate OAuth state and provider match.
        
        Args:
            state: State token to validate
            provider: OAuth provider name
            
        Returns:
            True if state is valid and matches provider, False otherwise
        """
        if not state:
            return False
        
        db_oauth_state = self.oauth_state_dao.get_state_by_token(state)
        if not db_oauth_state:
            return False
        
        # Check if state is expired
        if db_oauth_state.is_expired:
            # Clean up expired state
            self.oauth_state_dao.delete_state_by_token(state)
            return False
        
        # Check provider match
        if db_oauth_state.provider != provider:
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
        db_oauth_state = self.oauth_state_dao.get_state_by_token(state)
        if not db_oauth_state:
            raise InvalidStateError(f"State not found: {state}")
        
        # Check expiration
        if db_oauth_state.is_expired:
            # Clean up expired state
            self.oauth_state_dao.delete_state_by_token(state)
            raise InvalidStateError(f"State expired: {state}")
        
        return db_oauth_state.meta_data

    def get_state_data(self, state: str) -> Optional[DBOAuthState]:
        """
        Get complete OAuth state data.
        
        Args:
            state: State token
            
        Returns:
            DBOAuthState object if state exists and is valid, None otherwise
        """
        db_oauth_state = self.oauth_state_dao.get_state_by_token(state)
        if not db_oauth_state:
            return None
        
        # Check expiration
        if db_oauth_state.is_expired:
            # Clean up expired state
            self.oauth_state_dao.delete_state_by_token(state)
            return None
        
        return db_oauth_state
    
    def remove_state(self, state: str) -> bool:
        """
        Remove a stored state.
        
        Args:
            state: State token to remove
            
        Returns:
            True if state was removed, False if not found
        """
        return self.oauth_state_dao.delete_state_by_token(state)

    def cleanup_expired_states(self) -> int:
        """
        Remove all expired states from storage.
        
        Returns:
            Number of expired states removed
        """
        return self.oauth_state_dao.cleanup_expired_states()
    
    def __contains__(self, state: str) -> bool:
        """Check if state exists in storage."""
        db_state = self.oauth_state_dao.get_state_by_token(state)
        return db_state is not None and not db_state.is_expired