import os
import time
import shutil
from fastapi import UploadFile
from core.logging import get_logger
from services.indexing_service import IndexingService
from schemas.upload import UploadResponse

logger = get_logger(__name__)

class UploadService:
    """Service to handle file persistence and trigger indexing."""

    UPLOAD_DIR = "./uploads"

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def process_uploads(self, files: list[UploadFile]) -> UploadResponse:
        """
        Saves uploaded files and triggers the incremental indexing pipeline.
        Assumes basic validation (extensions, non-empty) is handled by the route.
        """
        logger.info(f"UploadService: Processing {len(files)} uploaded files.")
        start_time = time.perf_counter()

        # Save files securely
        for file in files:
            file_path = os.path.join(self.UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"Saved file {file.filename} to {self.UPLOAD_DIR}")

        # Trigger indexing
        logger.info("UploadService: Triggering IndexingService.")
        indexing_service = IndexingService()
        stats = indexing_service.run_incremental_update()

        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000

        # Build response message
        processed_count = len(stats["processed_files"])
        skipped_count = len(stats["skipped_files"])
        doc_count = stats["indexed_documents_count"]

        if processed_count > 0:
            message = f"Successfully uploaded and indexed {processed_count} file(s), creating {doc_count} documents."
        else:
            message = "Files uploaded successfully but no new files were indexed (all were skipped/duplicates)."

        logger.info(f"UploadService: Finished processing in {processing_time_ms:.2f}ms. {message}")

        return UploadResponse(
            uploaded_files=stats["processed_files"],
            skipped_files=stats["skipped_files"],
            indexed_documents=doc_count,
            processing_time_ms=processing_time_ms,
            message=message
        )
