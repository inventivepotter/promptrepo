"""
Factory for creating configuration strategies based on hosting type.
Implements a registry pattern for extensibility.
"""

import os
from typing import Type, Dict, List
from schemas.config import AppConfig
from .config_base import ConfigBase
from schemas.config import HostingType
from .individual_strategy import IndividualConfig
from .organization_strategy import OrganizationConfig
from .multi_tenant_strategy import MultiTenantConfig


class ConfigStrategyFactory:
    """
    Factory for creating configuration strategies based on hosting type.
    Implements a registry pattern for extensibility.
    """
    
    # Registry of available strategies
    _strategies: Dict[HostingType, Type[ConfigBase]] = {
        HostingType.INDIVIDUAL: IndividualConfig,
        HostingType.ORGANIZATION: OrganizationConfig,
        HostingType.MULTI_TENANT: MultiTenantConfig
    }
    
    @classmethod
    def get_strategy(cls) -> ConfigBase:
        """
        Create appropriate configuration strategy for the hosting type.
            
        Returns:
            ConfigBase: The appropriate strategy instance
            
        Raises:
            ValueError: If hosting type is not supported
        """
        hosting_type = os.environ.get("HOSTING_TYPE", "individual")
        try:
            hosting_type_enum = HostingType(hosting_type)
        except ValueError:
            raise ValueError(f"Unsupported hosting type: {hosting_type}")
        
        strategy_class = cls._strategies.get(hosting_type_enum)
        if not strategy_class:
            raise ValueError(f"Unsupported hosting type: {hosting_type}")
        
        return strategy_class()
    
    @classmethod
    def register_strategy(cls, hosting_type: HostingType, strategy_class: Type[ConfigBase]) -> None:
        """
        Register a new strategy for a hosting type.
        Enables runtime extension of supported hosting types.
        
        Args:
            hosting_type: The hosting type identifier
            strategy_class: The strategy class to register
        """
        cls._strategies[hosting_type] = strategy_class
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """
        Get list of all supported hosting types.
        
        Returns:
            List[str]: List of supported hosting type identifiers
        """
        return HostingType._member_names_