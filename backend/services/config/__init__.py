"""
Configuration service module using Strategy Pattern for hosting type management.

This module provides a refactored configuration service that eliminates if-else chains
through the use of Strategy Pattern and Factory Pattern.
"""
from .config_factory import ConfigStrategyFactory
from .config_service import ConfigService
from .config_interface import IConfig
from .strategies.individual import IndividualConfig
from .strategies.organization import OrganizationConfig
# Export the main ConfigService class and instance
__all__ = [
    'ConfigStrategyFactory',
    'IConfig',
    'ConfigService',
    'IndividualConfig',
    'OrganizationConfig'
]