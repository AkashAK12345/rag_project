"""
connectors/connector_registry.py

Registry pattern for resolving string identifiers (e.g. 'sql') to 
Connector classes, following the Open/Closed Principle.
"""

from typing import Dict, Type
from connectors.base_connector import BaseConnector


class ConnectorRegistry:
    """
    Central registry for available connectors.
    Connectors should register themselves here to avoid large if/else blocks.
    """
    
    _registry: Dict[str, Type[BaseConnector]] = {}

    @classmethod
    def register(cls, source_type: str, connector_class: Type[BaseConnector]) -> None:
        """Register a new connector class for a source_type identifier."""
        cls._registry[source_type.lower()] = connector_class

    @classmethod
    def get(cls, source_type: str) -> Type[BaseConnector]:
        """Retrieve the connector class for the given source_type."""
        connector_class = cls._registry.get(source_type.lower())
        if not connector_class:
            raise ValueError(f"Unknown connector source_type: {source_type}")
        return connector_class
