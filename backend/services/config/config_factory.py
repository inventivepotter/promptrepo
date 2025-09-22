"""
Factory for creating configuration strategies based on hosting type.
Implements a registry pattern for extensibility.
"""

import os
from typing import Type, Dict, List
from services.config.models import HostingType
from services.config.config_interface import IConfig
from services.config.strategies.individual import IndividualConfig
from services.config.strategies.organization import OrganizationConfig


class ConfigStrategyFactory:
    """
    Factory for creating configuration strategies based on hosting type.
    Implements a registry pattern for extensibility.
    """
    
    # Registry of available strategies
    _strategies: Dict[HostingType, Type[IConfig]] = {
        HostingType.INDIVIDUAL: IndividualConfig,
        HostingType.ORGANIZATION: OrganizationConfig
    }
    
    @classmethod
    def get_strategy(cls) -> IConfig:
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
    def get_supported_types(cls) -> List[str]:
        """
        Get list of all supported hosting types.
        
        Returns:
            List[str]: List of supported hosting type identifiers
        """
        return HostingType._member_names_