"""
connectors/connector_manager.py

Orchestrates connector lifecycle, validation, execution, and error handling.
"""

from typing import Any, Dict
from core.logging import get_logger
from schemas.connector_result import ConnectorResult
from connectors.connector_factory import ConnectorFactory

logger = get_logger(__name__)


class ConnectorManager:
    """
    Manages the execution of a connector config.
    """

    @staticmethod
    def execute(
        source_type: str, 
        config: Dict[str, Any], 
        connector_id: str | None = None, 
        organization_id: str | None = None,
        sync_token: str | None = None
    ) -> ConnectorResult:
        """
        Instantiate, connect, validate, fetch, and disconnect a connector.
        
        Args:
            source_type: e.g. 'sql', 'rest', 'excel'
            config: Dictionary containing config (from DB or API payload)
            connector_id: ID of the connector config if from DB
            organization_id: Enterprise tenant ID
            sync_token: Optional token for incremental sync
            
        Returns:
            ConnectorResult (containing DataFrames and metadata)
            
        Raises:
            Exception: If validation or fetch fails critically.
        """
        logger.info(f"ConnectorManager: orchestrating '{source_type}' connector (ID: {connector_id})")
        
        connector = ConnectorFactory.create(
            source_type=source_type, 
            config=config, 
            connector_id=connector_id,
            organization_id=organization_id
        )

        try:
            # 1. Connect
            connector.connect()

            # 2. Validate
            if not connector.validate():
                raise ValueError(f"Connector validation failed for source '{source_type}'")

            # 3. Fetch
            result: ConnectorResult = connector.fetch(sync_token=sync_token)
            
            logger.info(
                f"ConnectorManager: fetch complete. "
                f"Retrieved {result.record_count} records across {len(result.dataframes)} datasets."
            )
            
            if result.errors:
                logger.error(f"ConnectorManager: fetch reported {len(result.errors)} error(s).")
            if result.warnings:
                logger.warning(f"ConnectorManager: fetch reported {len(result.warnings)} warning(s).")

            return result

        except Exception as e:
            logger.error(f"ConnectorManager: execution failed - {str(e)}", exc_info=True)
            raise
            
        finally:
            # 4. Always Disconnect
            try:
                connector.disconnect()
            except Exception as e:
                logger.error(f"ConnectorManager: failed to disconnect - {str(e)}")
