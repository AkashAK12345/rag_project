import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from fastapi import UploadFile
from core.logging import get_logger
from services.job_manager import JobManager
from services.indexing_service import IndexingService
from schemas.jobs import JobRecord, JobStatus, JobAcceptedResponse

logger = get_logger(__name__)

UPLOAD_DIR = "./uploads"


class BackgroundJobService:
    """
    Coordinates the upload → save → index workflow as an async background job.

    Responsibilities:
    - Accept validated UploadFile list from the route.
    - Save file bytes to disk synchronously (fast, must complete before 202 is returned
      so the files exist when the background worker starts).
    - Create and register a JobRecord via JobManager.
    - Return the JobAcceptedResponse immediately to the caller.
    - Provide the runnable `execute_job` method that FastAPI's BackgroundTasks
      will invoke in a thread-pool worker after the HTTP response is sent.

    Decision: file saving happens BEFORE the 202 response.
    Reason: UploadFile.file is a SpooledTemporaryFile — it is only valid while
    the request is alive. If we deferred saving to the background worker, the
    file handles would be closed by the time the worker ran.
    """

    def __init__(self, job_manager: JobManager, rag_service=None) -> None:
        self._job_manager = job_manager
        self._rag_service = rag_service
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # Public interface called by the route
    # ------------------------------------------------------------------

    def accept_upload(self, files: list[UploadFile]) -> JobAcceptedResponse:
        """
        Saves files to disk and creates a QUEUED job.
        Returns the 202 payload; the caller is responsible for scheduling
        `execute_job` via FastAPI BackgroundTasks.
        """
        job_id = str(uuid.uuid4())
        saved_filenames: list[str] = []

        # --- SAVING_FILES (synchronous, must finish before response is sent) ---
        for file in files:
            dest = os.path.join(UPLOAD_DIR, file.filename)
            with open(dest, "wb") as buf:
                shutil.copyfileobj(file.file, buf)
            saved_filenames.append(file.filename)
            logger.info(f"Job {job_id}: saved '{file.filename}' to {UPLOAD_DIR}")

        # --- Register job in QUEUED state ---
        job = JobRecord(
            job_id=job_id,
            status=JobStatus.QUEUED,
            uploaded_files=saved_filenames,
            created_at=datetime.now(timezone.utc),
        )
        self._job_manager.register(job)
        logger.info(f"Job {job_id}: created with status QUEUED for {len(saved_filenames)} file(s).")

        return JobAcceptedResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message=f"Indexing job created. {len(saved_filenames)} file(s) queued for background processing.",
        )

    # ------------------------------------------------------------------
    # Background worker — called by FastAPI BackgroundTasks in a thread
    # ------------------------------------------------------------------

    def execute_job(self, job_id: str) -> None:
        """
        The actual indexing logic executed by the background thread.
        Transitions the job through: QUEUED → INDEXING → COMPLETED | FAILED.
        Progress is reported to JobManager at each significant checkpoint.
        """
        logger.info(f"Job {job_id}: background worker started.")

        # Transition → INDEXING
        started_at = datetime.now(timezone.utc)
        self._job_manager.update_status(
            job_id=job_id,
            status=JobStatus.INDEXING,
            progress_percentage=10.0,
            started_at=started_at,
        )

        wall_start = time.perf_counter()
        
        job = self._job_manager.get(job_id)
        if not job:
            logger.error(f"Job {job_id}: could not be found in JobManager during execution.")
            return

        try:
            from services.ingestion_service import IngestionService
            ingestion_service = IngestionService()
            
            total_files = len(job.uploaded_files)
            processed_count = 0
            indexed_documents = 0
            skipped_files = []
            processed_files = []

            for filename in job.uploaded_files:
                file_path = os.path.join(UPLOAD_DIR, filename)
                
                base_progress = 10.0 + (processed_count / total_files) * 80.0
                file_progress_weight = 80.0 / total_files if total_files > 0 else 0
                
                def update_progress(indexed_so_far: int, doc_count: int):
                    if doc_count > 0:
                        file_pct = indexed_so_far / doc_count
                        current_progress = base_progress + (file_pct * file_progress_weight)
                        self._job_manager.update_status(
                            job_id=job_id,
                            status=JobStatus.INDEXING,
                            progress_percentage=current_progress,
                            indexed_documents=indexed_documents + indexed_so_far
                        )

                # Progress checkpoint
                self._job_manager.update_status(
                    job_id=job_id,
                    status=JobStatus.INDEXING,
                    progress_percentage=base_progress,
                )

                try:
                    result = ingestion_service.process_file(file_path, progress_callback=update_progress)
                    indexed_documents += result.document_count
                    processed_files.append(filename)
                    
                    if result.capability_graph:
                        from services.capability_service import CapabilityService
                        CapabilityService().repository.save(job_id + "_" + filename, result.capability_graph)
                except Exception as e:
                    logger.warning(f"Job {job_id}: file '{filename}' failed ingestion: {e}")
                    skipped_files.append(filename)
                    
                processed_count += 1

            wall_ms = (time.perf_counter() - wall_start) * 1000
            completed_at = datetime.now(timezone.utc)

            self._job_manager.update_status(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress_percentage=100.0,
                completed_at=completed_at,
                uploaded_files=processed_files,
                indexed_documents=indexed_documents,
                skipped_files=skipped_files,
                processing_time_ms=round(wall_ms, 2),
            )
            
            if self._rag_service:
                self._rag_service.reload_index()
                
            logger.info(
                f"Job {job_id}: COMPLETED — {indexed_documents} docs indexed, "
                f"{len(skipped_files)} skipped, {wall_ms:.1f}ms."
            )

        except Exception as exc:
            wall_ms = (time.perf_counter() - wall_start) * 1000
            completed_at = datetime.now(timezone.utc)

            self._job_manager.update_status(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress_percentage=0.0,
                completed_at=completed_at,
                processing_time_ms=round(wall_ms, 2),
                error_message=str(exc),
            )
            logger.error(f"Job {job_id}: FAILED — {exc}", exc_info=True)

    # ------------------------------------------------------------------
    # Background worker for Enterprise Connector Syncs
    # ------------------------------------------------------------------

    def execute_sync_job(self, job_id: str) -> None:
        """
        Executes a background sync job for an Enterprise Connector.
        """
        logger.info(f"Sync Job {job_id}: background worker started.")

        started_at = datetime.now(timezone.utc)
        self._job_manager.update_status(
            job_id=job_id,
            status=JobStatus.INDEXING,
            progress_percentage=10.0,
            started_at=started_at,
        )

        wall_start = time.perf_counter()
        job = self._job_manager.get(job_id)
        if not job or not job.connector_id:
            logger.error(f"Sync Job {job_id}: missing job or connector_id.")
            return

        from models.user import SessionLocal
        from services.connector_service import ConnectorService
        from connectors.connector_manager import ConnectorManager
        from services.ingestion_service import IngestionService
        from models.connector import SyncHistoryModel
        from schemas.connector_status import SyncStatus

        db = SessionLocal()
        try:
            connector_service = ConnectorService(db)
            connector = connector_service.get_connector(job.connector_id)
            if not connector:
                raise ValueError(f"Connector {job.connector_id} not found in database.")

            # Progress -> 30% (Validation/Fetch Phase)
            self._job_manager.update_status(
                job_id=job_id,
                status=JobStatus.INDEXING,
                progress_percentage=30.0,
            )

            # 1. Fetch data via ConnectorManager
            result = ConnectorManager.execute(
                source_type=connector.source_type,
                config=connector.config,
                connector_id=connector.id,
                organization_id=connector.organization_id,
                sync_token=connector.sync_token,
            )

            def update_sync_progress(indexed_so_far: int, doc_count: int):
                if doc_count > 0:
                    file_pct = indexed_so_far / doc_count
                    current_progress = 70.0 + (file_pct * 30.0)
                    self._job_manager.update_status(
                        job_id=job_id,
                        status=JobStatus.INDEXING,
                        progress_percentage=current_progress,
                        indexed_documents=indexed_so_far
                    )

            # Progress -> 70% (Ingestion Phase)
            self._job_manager.update_status(
                job_id=job_id,
                status=JobStatus.INDEXING,
                progress_percentage=70.0,
            )

            # 2. Ingest Dataframes via IngestionService
            ingestion_service = IngestionService()
            report_result = ingestion_service.process_connector_result(result, progress_callback=update_sync_progress)
            
            if report_result and report_result.capability_graph:
                from services.capability_service import CapabilityService
                CapabilityService().repository.save(job_id + "_" + connector.id, report_result.capability_graph)
            
            # Update DB Connector state
            connector.last_sync_time = datetime.now(timezone.utc)
            # If the connector returned a new sync_token in metadata, we could update it here.
            # e.g., connector.sync_token = result.metadata.get("next_sync_token")
            
            # Update DB Sync History
            sync_history = db.query(SyncHistoryModel).filter(SyncHistoryModel.id == job_id).first()
            if sync_history:
                sync_history.status = SyncStatus.COMPLETED.value
                sync_history.records_imported = result.record_count
                sync_history.completed_at = datetime.now(timezone.utc)
                sync_history.processing_time_ms = (time.perf_counter() - wall_start) * 1000

            db.commit()

            wall_ms = (time.perf_counter() - wall_start) * 1000
            self._job_manager.update_status(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress_percentage=100.0,
                completed_at=datetime.now(timezone.utc),
                indexed_documents=report_result.document_count if report_result else 0,
                processing_time_ms=round(wall_ms, 2),
            )
            
            if self._rag_service:
                self._rag_service.reload_index()
                
            logger.info(f"Sync Job {job_id}: COMPLETED — {result.record_count} records retrieved, {wall_ms:.1f}ms.")

        except Exception as exc:
            db.rollback()
            wall_ms = (time.perf_counter() - wall_start) * 1000
            
            # Update DB Sync History
            sync_history = db.query(SyncHistoryModel).filter(SyncHistoryModel.id == job_id).first()
            if sync_history:
                sync_history.status = SyncStatus.FAILED.value
                sync_history.completed_at = datetime.now(timezone.utc)
                sync_history.processing_time_ms = wall_ms
                sync_history.error_message = str(exc)
            db.commit()

            self._job_manager.update_status(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress_percentage=0.0,
                completed_at=datetime.now(timezone.utc),
                processing_time_ms=round(wall_ms, 2),
                error_message=str(exc),
            )
            logger.error(f"Sync Job {job_id}: FAILED — {exc}", exc_info=True)
        finally:
            db.close()
