"""
schemas/sync_job.py

Data structures defining Sync Operations for Connectors.
"""
from enum import Enum
from pydantic import BaseModel


class SyncType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    INCREMENTAL = "incremental"
    FULL = "full"


class SyncRequest(BaseModel):
    """Payload to trigger a sync for a specific connector."""
    sync_type: SyncType = SyncType.MANUAL
    
class SyncResponse(BaseModel):
    """Response returned when a sync job is queued."""
    job_id: str
    connector_id: str
    status: str
    message: str
