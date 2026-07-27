import os
import shutil
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from schemas.ingestion import IngestionResponse
from services.ingestion_service import IngestionService
from api.dependencies import require_roles, get_rag_service
from models.user import Role
from services.rag_service import RagService
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}
UPLOAD_DIR = "./uploads"


@router.post(
    "",
    response_model=IngestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Synchronously ingest a single business report",
    description=(
        "Uploads and processes a single report (CSV or Excel). "
        "The file is parsed through the Unified Business Data Ingestion Framework, "
        "and immediately indexed. Use /upload for asynchronous batch processing."
    ),
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
)
def ingest_file(
    file: UploadFile = File(...),
    rag_service: RagService = Depends(get_rag_service)
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A file without a filename was uploaded.",
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Ingestion rejected: invalid extension for '{file.filename}'.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{ext}'. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(dest, "wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except Exception as e:
        logger.error(f"Failed to save uploaded file '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file.",
        )

    try:
        service = IngestionService()
        result = service.process_file(dest)
        
        rag_service.reload_index()
        
        return IngestionResponse(
            filename=file.filename,
            report_type=result.report_type,
            report_name=result.report_name,
            business_domain=result.business_domain,
            source_type=result.source_type,
            document_count=result.document_count,
            reporting_period=result.reporting_period,
            message="File successfully ingested and indexed.",
        )
    except ValueError as ve:
        logger.warning(f"Validation error during ingestion: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as e:
        logger.error(f"Error during ingestion of '{file.filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during ingestion.",
        )
