"""
schemas/connector_status.py

Status tracking for Connectors and their sync executions.
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConnectorStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class SyncStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncHistoryResponse(BaseModel):
    id: str
    connector_id: str
    sync_type: str
    status: SyncStatus
    records_imported: int
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    processing_time_ms: float

    class Config:
        from_attributes = True
