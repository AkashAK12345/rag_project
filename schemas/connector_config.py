"""
schemas/connector_config.py

Pydantic schemas for validating connector configurations.
Using Pydantic here because these payloads come directly from the API layer.
"""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AuthType(str, Enum):
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"


class SQLConfig(BaseModel):
    """Configuration for connecting to a SQL database."""
    connection_string: str = Field(..., description="SQLAlchemy compatible connection string (secrets should be injected via env in production).")
    query: str = Field(..., description="SQL query to execute to fetch the dataset.")


class RESTConfig(BaseModel):
    """Configuration for connecting to a REST API."""
    base_url: str = Field(..., description="Base URL of the API.")
    endpoint: str = Field(..., description="Specific endpoint to fetch data from.")
    method: str = Field("GET", description="HTTP method (GET/POST).")
    headers: Dict[str, str] = Field(default_factory=dict)
    query_params: Dict[str, str] = Field(default_factory=dict)
    
    auth_type: AuthType = Field(default=AuthType.NONE)
    auth_credentials: Dict[str, str] = Field(
        default_factory=dict, 
        description="Keys depend on auth_type (e.g., 'username'/'password' or 'token')"
    )
    
    # Pagination
    pagination_enabled: bool = Field(False)
    pagination_type: str = Field("offset", description="offset, cursor, or page")
    pagination_params: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Configuration for pagination fields (e.g., limit_key, offset_key)"
    )


class ConnectorCreate(BaseModel):
    """Payload for creating a new connector via API."""
    name: str = Field(..., description="Human-readable name for this connector.")
    source_type: str = Field(..., description="e.g., 'sql', 'rest', 'excel'")
    organization_id: Optional[str] = None
    config: Dict[str, Any] = Field(..., description="Connector-specific configuration (SQLConfig or RESTConfig dict).")


class ConnectorResponse(BaseModel):
    """Response payload for a connector."""
    id: str
    name: str
    source_type: str
    organization_id: Optional[str]
    config: Dict[str, Any]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
