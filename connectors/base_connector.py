"""
connectors/base_connector.py

Abstract interface for all Enterprise Connectors.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from schemas.connector_result import ConnectorResult


class BaseConnector(ABC):
    """
    Contract for every data connector (SQL, REST, API, etc.).
    
    A Connector translates a specific external system's API/protocol into
    a standardised ConnectorResult containing Pandas DataFrames.
    Connectors have ZERO business logic; they do not know what the data means.
    """

    def __init__(self, config: Dict[str, Any], connector_id: str | None = None, organization_id: str | None = None) -> None:
        self.config = config
        self.connector_id = connector_id
        self.organization_id = organization_id

    @abstractmethod
    def connect(self) -> None:
        """Establish connection or session with the external system."""
        ...

    @abstractmethod
    def validate(self) -> bool:
        """Validate that the configuration and connection are working."""
        ...

    @abstractmethod
    def fetch(self, sync_token: str | None = None) -> ConnectorResult:
        """
        Fetch data from the source system.
        
        Args:
            sync_token: Optional token (timestamp, cursor, ID) for incremental sync.
            
        Returns:
            ConnectorResult containing DataFrames.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Clean up resources, close connections, etc."""
        ...
