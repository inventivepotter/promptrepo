"""
Configuration service module using Strategy Pattern for hosting type management.

This module provides a refactored configuration service that eliminates if-else chains
through the use of Strategy Pattern and Factory Pattern.
"""

from .config_service import ConfigService
from .factory import ConfigStrategyFactory
from .config_base import ConfigBase

# Create a singleton instance for backward compatibility
config_service = ConfigService()

# Export the main ConfigService class and instance
__all__ = [
    'ConfigService',
    'ConfigStrategyFactory',
    'ConfigBase',
    'config_service',
]