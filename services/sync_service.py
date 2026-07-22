"""
services/sync_service.py

Orchestrates synchronization of Enterprise Connectors via BackgroundJobs.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from core.logging import get_logger
from models.connector import SyncHistoryModel
from schemas.jobs import JobRecord, JobStatus, JobAcceptedResponse
from schemas.sync_job import SyncType, SyncRequest, SyncResponse
from services.job_manager import JobManager
from services.connector_service import ConnectorService

logger = get_logger(__name__)


class SyncService:
    """
    Service to manage the execution of connector synchronizations.
    Reuses the existing JobManager to track running tasks.
    """

    def __init__(self, db: Session, job_manager: JobManager):
        self.db = db
        self.job_manager = job_manager
        self.connector_service = ConnectorService(db)

    def enqueue_sync(self, connector_id: str, request: SyncRequest) -> SyncResponse:
        """
        Creates a sync history record and enqueues the job.
        Returns immediately.
        """
        connector = self.connector_service.get_connector(connector_id)
        if not connector:
            raise ValueError(f"Connector {connector_id} not found.")

        job_id = str(uuid.uuid4())
        
        # 1. Create Sync History Record (DB)
        sync_history = SyncHistoryModel(
            id=job_id,
            connector_id=connector_id,
            sync_type=request.sync_type.value,
        )
        self.db.add(sync_history)
        self.db.commit()

        # 2. Register Job in Memory (JobManager)
        job = JobRecord(
            job_id=job_id,
            connector_id=connector_id,
            status=JobStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
        )
        self.job_manager.register(job)
        
        logger.info(f"SyncService: queued sync job {job_id} for connector {connector_id}")

        return SyncResponse(
            job_id=job_id,
            connector_id=connector_id,
            status="queued",
            message=f"Sync job queued for connector '{connector.name}'"
        )
