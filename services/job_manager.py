import threading
from datetime import datetime
from typing import Dict, List
from core.logging import get_logger
from schemas.jobs import JobRecord, JobStatus

logger = get_logger(__name__)


class JobManager:
    """
    Thread-safe, in-memory registry for background indexing jobs.

    Design decision: a threading.Lock guards every read and write so that
    the FastAPI async event loop thread (handling API requests) and the
    worker thread (running IndexingService) can never corrupt shared state.
    This is the ONLY place jobs are mutated — BackgroundJobService delegates
    all state transitions here.

    JobManager is an in-memory registry. Jobs are lost upon server restart, 
    the frontend must handle lost job states gracefully, and completed 
    job history does not persist across restarts.
    """

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def register(self, job: JobRecord) -> None:
        """Add a newly created job to the registry."""
        with self._lock:
            self._jobs[job.job_id] = job
        logger.info(f"JobManager: registered job {job.job_id}")

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress_percentage: float | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        uploaded_files: list[str] | None = None,
        indexed_documents: int | None = None,
        skipped_files: list[str] | None = None,
        processing_time_ms: float | None = None,
        error_message: str | None = None,
    ) -> None:
        """
        Apply a partial state update to an existing job.
        Only non-None keyword arguments overwrite the stored value.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                logger.warning(f"JobManager: attempted to update unknown job {job_id}")
                return
            # Pydantic v2: model_copy(update=...) is the idiomatic approach
            patch: dict = {"status": status}
            if progress_percentage is not None:
                patch["progress_percentage"] = progress_percentage
            if started_at is not None:
                patch["started_at"] = started_at
            if completed_at is not None:
                patch["completed_at"] = completed_at
            if uploaded_files is not None:
                patch["uploaded_files"] = uploaded_files
            if indexed_documents is not None:
                patch["indexed_documents"] = indexed_documents
            if skipped_files is not None:
                patch["skipped_files"] = skipped_files
            if processing_time_ms is not None:
                patch["processing_time_ms"] = processing_time_ms
            if error_message is not None:
                patch["error_message"] = error_message
            self._jobs[job_id] = job.model_copy(update=patch)

    def delete(self, job_id: str) -> bool:
        """Remove a completed or failed job. Returns False if not found."""
        with self._lock:
            if job_id not in self._jobs:
                return False
            del self._jobs[job_id]
        logger.info(f"JobManager: deleted job {job_id}")
        return True

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, job_id: str) -> JobRecord | None:
        """Return a job snapshot (a copy), or None if not found."""
        with self._lock:
            job = self._jobs.get(job_id)
            return job.model_copy() if job else None

    def list_all(self) -> List[JobRecord]:
        """Return a snapshot of every tracked job."""
        with self._lock:
            return [j.model_copy() for j in self._jobs.values()]

    def is_active(self, job_id: str) -> bool:
        """True if the job is in a non-terminal state (not completed/failed)."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return False
            return job.status not in (JobStatus.COMPLETED, JobStatus.FAILED)
