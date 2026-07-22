from fastapi import APIRouter, Depends, HTTPException, status
from schemas.jobs import JobRecord, JobListResponse
from services.job_manager import JobManager
from api.dependencies import get_job_manager, require_roles
from models.user import Role
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])


@router.get(
    "",
    response_model=JobListResponse,
    summary="List all background jobs",
    description="Returns every background indexing job currently tracked in memory.",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
)
async def list_jobs(job_manager: JobManager = Depends(get_job_manager)):
    jobs = job_manager.list_all()
    return JobListResponse(total=len(jobs), jobs=jobs)


@router.get(
    "/{job_id}",
    response_model=JobRecord,
    summary="Get a specific background job",
    description="Returns the full state of a single background indexing job by its UUID.",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
)
async def get_job(job_id: str, job_manager: JobManager = Depends(get_job_manager)):
    job = job_manager.get(job_id)
    if not job:
        logger.warning(f"GET /jobs/{job_id}: job not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a completed or failed job",
    description="Removes a terminated job from the in-memory registry. Returns 409 if still active.",
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
async def delete_job(job_id: str, job_manager: JobManager = Depends(get_job_manager)):
    if job_manager.is_active(job_id):
        logger.warning(f"DELETE /jobs/{job_id}: attempted to delete an active job.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job '{job_id}' is still active and cannot be deleted.",
        )
    deleted = job_manager.delete(job_id)
    if not deleted:
        logger.warning(f"DELETE /jobs/{job_id}: job not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    logger.info(f"DELETE /jobs/{job_id}: job deleted successfully.")
