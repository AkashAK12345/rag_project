from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class JobStatus(str, Enum):
    """Lifecycle states of a background indexing job."""
    QUEUED = "queued"
    VALIDATING = "validating"
    SAVING_FILES = "saving_files"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRecord(BaseModel):
    """Full representation of a background indexing job."""
    job_id: str = Field(..., description="UUID of the job.")
    connector_id: str | None = Field(default=None, description="ID of the Connector, if this job is a sync job.")
    status: JobStatus = Field(..., description="Current lifecycle state of the job.")
    progress_percentage: float = Field(0.0, description="Approximate percentage completion (0–100).")
    uploaded_files: list[str] = Field(default_factory=list, description="Files saved and passed to the indexer.")
    indexed_documents: int = Field(0, description="Total documents indexed so far.")
    skipped_files: list[str] = Field(default_factory=list, description="Files skipped because they were already indexed.")
    created_at: datetime = Field(..., description="Timestamp when the job was created.")
    started_at: datetime | None = Field(default=None, description="Timestamp when the indexer began processing.")
    completed_at: datetime | None = Field(default=None, description="Timestamp when the job finished (success or failure).")
    processing_time_ms: float | None = Field(default=None, description="Total wall-clock time of the indexing phase in milliseconds.")
    error_message: str | None = Field(default=None, description="Error detail if the job failed.")


class JobAcceptedResponse(BaseModel):
    """HTTP 202 response returned immediately when an upload is accepted."""
    job_id: str = Field(..., description="UUID of the created background job.")
    status: JobStatus = Field(..., description="Initial status (always 'queued').")
    message: str = Field(..., description="Human-readable confirmation message.")


class JobListResponse(BaseModel):
    """Response payload for GET /jobs."""
    total: int = Field(..., description="Total number of jobs in registry.")
    jobs: list[JobRecord] = Field(..., description="All tracked job records.")
