from typing import List, Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import WithJsonSchema
from schemas.jobs import JobAcceptedResponse
from services.background_job_service import BackgroundJobService
from services.job_manager import JobManager
from api.dependencies import get_job_manager, require_roles, get_rag_service
from models.user import Role
from services.rag_service import RagService
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


@router.post(
    "",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload and asynchronously index Excel reports",
    description=(
        "Accepts one or more Excel files (.xlsx, .xls). "
        "Files are saved immediately, and indexing is scheduled as a background job. "
        "Returns HTTP 202 Accepted with a job_id to poll for status."
    ),
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
)
async def upload_files(
    background_tasks: BackgroundTasks,
    # NOTE:
    # This schema override exists solely to restore the Swagger UI
    # multi-file picker.
    #
    # FastAPI generates a valid OpenAPI 3.1 schema using
    # `contentMediaType`, but the bundled Swagger UI currently renders
    # arrays of UploadFile as `array<string>` instead of file inputs.
    #
    # Remove this workaround once the upstream Swagger UI issue is resolved.
    files: list[
        Annotated[
            UploadFile,
            WithJsonSchema({"type": "string", "format": "binary"})
        ]
    ] = File(...),
    job_manager: JobManager = Depends(get_job_manager),
    rag_service: RagService = Depends(get_rag_service),
):
    logger.info(f"Upload request received: {len(files)} file(s).")

    if not files:
        logger.warning("Upload rejected: empty file list.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were provided in the request.",
        )

    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file without a filename was uploaded.",
            )
        is_valid = any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
        if not is_valid:
            logger.warning(f"Upload rejected: invalid extension for '{file.filename}'.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type for '{file.filename}'. Only .xlsx, .xls, and .csv are accepted.",
            )

    try:
        job_service = BackgroundJobService(job_manager=job_manager, rag_service=rag_service)
        accepted = job_service.accept_upload(files)
        background_tasks.add_task(job_service.execute_job, accepted.job_id)
        logger.info(f"Upload accepted: job {accepted.job_id} queued for background indexing.")
        return accepted
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to accept upload: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while accepting the upload.",
        )
