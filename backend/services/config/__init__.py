"""
Configuration service module using Strategy Pattern for hosting type management.

This module provides a refactored configuration service that eliminates if-else chains
through the use of Strategy Pattern and Factory Pattern.
"""
from .factory import ConfigStrategyFactory
from .config_interface import IConfig
from .individual_strategy import IndividualConfig
from .organization_strategy import OrganizationConfig
from .multi_tenant_strategy import MultiTenantConfig
from .config_service import ConfigService

# Export the main ConfigService class and instance
__all__ = [
    'ConfigStrategyFactory',
    'IConfig',
    'ConfigService',
    'IndividualConfig',
    'OrganizationConfig',
    'MultiTenantConfig'
]