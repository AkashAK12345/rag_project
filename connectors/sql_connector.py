"""
connectors/sql_connector.py

Generic SQL Connector implementation.
Built around a query execution abstraction rather than directly coupling to pandas.read_sql.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Any, Dict

from schemas.report import SourceType
from schemas.connector_result import ConnectorResult
from connectors.base_connector import BaseConnector
from connectors.connector_registry import ConnectorRegistry


class SQLConnector(BaseConnector):
    """
    Connects to any SQL database supported by SQLAlchemy.
    """
    
    def __init__(self, config: Dict[str, Any], connector_id: str | None = None, organization_id: str | None = None) -> None:
        super().__init__(config, connector_id, organization_id)
        self.connection_string = self.config.get("connection_string")
        self.query = self.config.get("query")
        self._engine: Engine | None = None
        self._connection = None

    def connect(self) -> None:
        if not self.connection_string:
            raise ValueError("connection_string is missing from config")
        if not self.query:
            raise ValueError("query is missing from config")
        
        # In a real enterprise system, secrets should be resolved here from a vault
        self._engine = create_engine(self.connection_string)
        self._connection = self._engine.connect()

    def validate(self) -> bool:
        if not self._connection:
            return False
        try:
            # Simple ping
            self._connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def fetch(self, sync_token: str | None = None) -> ConnectorResult:
        query_to_execute = self.query
        
        # Very basic incremental logic implementation for demonstration
        if sync_token:
            # Assumes query has a placeholder for sync_token (e.g. last updated timestamp)
            # In a full implementation, query parsing/formatting would be more robust
            if "{sync_token}" in query_to_execute:
                query_to_execute = query_to_execute.format(sync_token=sync_token)

        result_proxy = self._connection.execute(text(query_to_execute))
        
        # Convert SQLAlchemy result rows to Pandas DataFrame (abstracting pandas.read_sql)
        columns = list(result_proxy.keys())
        rows = result_proxy.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        
        dataset_name = self.config.get("dataset_name", "sql_query_result")
        
        return ConnectorResult(
            source_type=SourceType.SQL,
            organization_id=self.organization_id,
            connector_id=self.connector_id,
            dataset_name=dataset_name,
            dataframes={dataset_name: df},
            metadata={"query": query_to_execute}
        )

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()
        if self._engine:
            self._engine.dispose()


# Register connector
ConnectorRegistry.register("sql", SQLConnector)
