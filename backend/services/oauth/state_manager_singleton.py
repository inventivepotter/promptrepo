"""
OAuth State Manager Singleton

This module provides a singleton instance of StateManager to ensure
OAuth states persist across requests during development.

NOTE: This is a temporary solution for development. In production,
states should be persisted to a database or cache like Redis.
"""

from services.oauth.state_manager import StateManager

# Create a singleton instance that persists across requests
_state_manager_instance = None


def get_state_manager() -> StateManager:
    """
    Get the singleton StateManager instance.
    
    Returns:
        StateManager: The singleton state manager instance
    """
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = StateManager(state_expiry_minutes=10)
    return _state_manager_instance