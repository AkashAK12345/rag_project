"""
connectors/connector_factory.py

Factory for instantiating connectors dynamically.
"""

from typing import Any, Dict
from connectors.base_connector import BaseConnector
from connectors.connector_registry import ConnectorRegistry


class ConnectorFactory:
    """
    Creates connector instances using the Registry.
    """
    
    @staticmethod
    def create(source_type: str, config: Dict[str, Any], connector_id: str | None = None, organization_id: str | None = None) -> BaseConnector:
        """
        Instantiate the appropriate connector.
        
        Args:
            source_type: e.g. 'sql', 'rest', 'excel'
            config: Dictionary containing connector-specific configuration
            connector_id: Unique ID of the connector config
            organization_id: Organization this connector belongs to
            
        Returns:
            An instantiated BaseConnector.
        """
        connector_class = ConnectorRegistry.get(source_type)
        return connector_class(config=config, connector_id=connector_id, organization_id=organization_id)
