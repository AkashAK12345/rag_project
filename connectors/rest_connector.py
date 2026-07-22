"""
connectors/rest_connector.py

Generic REST API Connector implementation.
Supports pagination, authentication, and converts JSON to DataFrames.
"""

import pandas as pd
import requests
from typing import Any, Dict, List
import urllib.parse

from schemas.report import SourceType
from schemas.connector_result import ConnectorResult
from connectors.base_connector import BaseConnector
from connectors.connector_registry import ConnectorRegistry


class RESTConnector(BaseConnector):
    """
    Connects to REST APIs and fetches JSON data.
    """
    
    def __init__(self, config: Dict[str, Any], connector_id: str | None = None, organization_id: str | None = None) -> None:
        super().__init__(config, connector_id, organization_id)
        self.base_url = self.config.get("base_url", "")
        self.endpoint = self.config.get("endpoint", "")
        self.method = self.config.get("method", "GET").upper()
        self.headers = self.config.get("headers", {})
        self.query_params = self.config.get("query_params", {})
        
        self.auth_type = self.config.get("auth_type", "none")
        self.auth_credentials = self.config.get("auth_credentials", {})
        
        self.pagination_enabled = self.config.get("pagination_enabled", False)
        self.pagination_type = self.config.get("pagination_type", "offset")
        self.pagination_params = self.config.get("pagination_params", {})
        
        self._session = requests.Session()

    def connect(self) -> None:
        if not self.base_url or not self.endpoint:
            raise ValueError("base_url and endpoint are required for RESTConnector")
            
        # Configure authentication
        if self.auth_type == "bearer":
            token = self.auth_credentials.get("token")
            if token:
                self._session.headers.update({"Authorization": f"Bearer {token}"})
        elif self.auth_type == "api_key":
            key_name = self.auth_credentials.get("key_name", "X-API-Key")
            key_value = self.auth_credentials.get("key_value")
            if key_value:
                self._session.headers.update({key_name: key_value})
        elif self.auth_type == "basic":
            username = self.auth_credentials.get("username")
            password = self.auth_credentials.get("password")
            if username and password:
                self._session.auth = (username, password)
                
        self._session.headers.update(self.headers)

    def validate(self) -> bool:
        # A simple validation could be an OPTIONS or a ping endpoint if configured
        # For a generic connector, we assume configuration is structurally valid
        return True

    def fetch(self, sync_token: str | None = None) -> ConnectorResult:
        url = urllib.parse.urljoin(self.base_url, self.endpoint)
        params = self.query_params.copy()
        
        all_records: List[Dict[str, Any]] = []
        warnings = []
        
        try:
            if not self.pagination_enabled:
                response = self._session.request(self.method, url, params=params)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, list):
                    all_records.extend(data)
                elif isinstance(data, dict):
                    # Guessing data is in a key like 'data', 'items', 'records'
                    for key in ["data", "items", "records", "results"]:
                        if key in data and isinstance(data[key], list):
                            all_records.extend(data[key])
                            break
                    else:
                        all_records.append(data)
            else:
                all_records, warnings = self._fetch_paginated(url, params)
                
        except Exception as e:
            # We return empty df and an error instead of crashing if possible
            return ConnectorResult(
                source_type=SourceType.API,
                organization_id=self.organization_id,
                connector_id=self.connector_id,
                dataset_name=self.endpoint,
                dataframes={},
                errors=[str(e)]
            )
            
        df = pd.json_normalize(all_records)
        dataset_name = self.config.get("dataset_name", self.endpoint.strip("/").split("/")[-1] or "api_data")
        
        return ConnectorResult(
            source_type=SourceType.API,
            organization_id=self.organization_id,
            connector_id=self.connector_id,
            dataset_name=dataset_name,
            dataframes={dataset_name: df},
            warnings=warnings,
            metadata={"url": url, "records_fetched": len(all_records)}
        )

    def _fetch_paginated(self, url: str, params: Dict[str, str]) -> tuple[List[Dict[str, Any]], List[str]]:
        records = []
        warnings = []
        
        if self.pagination_type == "offset":
            limit_key = self.pagination_params.get("limit_key", "limit")
            offset_key = self.pagination_params.get("offset_key", "offset")
            limit = self.pagination_params.get("limit", 100)
            
            offset = 0
            while True:
                params[limit_key] = limit
                params[offset_key] = offset
                response = self._session.request(self.method, url, params=params)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("data", data.get("items", data.get("records", []))) if isinstance(data, dict) else data
                
                if not items or not isinstance(items, list):
                    break
                    
                records.extend(items)
                if len(items) < limit:
                    break
                offset += limit
                
                if len(records) > 10000:  # Circuit breaker for demo
                    warnings.append("Pagination circuit breaker hit at 10k records.")
                    break
                    
        return records, warnings

    def disconnect(self) -> None:
        self._session.close()


# Register connector
ConnectorRegistry.register("rest", RESTConnector)
ConnectorRegistry.register("api", RESTConnector)
