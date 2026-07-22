"""
api/connectors.py

API Endpoints for Enterprise Connector Management and Synchronization.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List

from models.user import SessionLocal, Role
from api.dependencies import require_roles, get_job_manager
from schemas.connector_config import ConnectorCreate, ConnectorResponse
from schemas.sync_job import SyncRequest, SyncResponse
from schemas.connector_status import SyncHistoryResponse
from services.connector_service import ConnectorService
from services.sync_service import SyncService
from services.job_manager import JobManager
from services.background_job_service import BackgroundJobService
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/connectors", tags=["Connectors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=ConnectorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
    summary="Create a new connector"
)
def create_connector(
    payload: ConnectorCreate, 
    db: Session = Depends(get_db)
):
    try:
        service = ConnectorService(db)
        connector = service.create_connector(payload)
        return connector
    except Exception as e:
        logger.error(f"Failed to create connector: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "",
    response_model=List[ConnectorResponse],
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.ANALYST))],
    summary="List all connectors"
)
def list_connectors(
    organization_id: str | None = None,
    db: Session = Depends(get_db)
):
    service = ConnectorService(db)
    return service.list_connectors(organization_id=organization_id)


@router.post(
    "/{connector_id}/sync",
    response_model=SyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
    summary="Trigger a background sync for a connector"
)
def trigger_sync(
    connector_id: str,
    payload: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    job_manager: JobManager = Depends(get_job_manager)
):
    try:
        sync_service = SyncService(db, job_manager)
        response = sync_service.enqueue_sync(connector_id, payload)
        
        # We spawn BackgroundJobService's execute_sync_job directly here
        bg_service = BackgroundJobService(job_manager)
        background_tasks.add_task(bg_service.execute_sync_job, response.job_id)
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to enqueue sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{connector_id}/history",
    response_model=List[SyncHistoryResponse],
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.ANALYST))],
    summary="Get sync history for a connector"
)
def get_sync_history(
    connector_id: str,
    db: Session = Depends(get_db)
):
    from models.connector import SyncHistoryModel
    history = db.query(SyncHistoryModel).filter(SyncHistoryModel.connector_id == connector_id).order_by(SyncHistoryModel.started_at.desc()).all()
    return history


@router.delete(
    "/{connector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(Role.ADMIN))],
    summary="Delete a connector"
)
def delete_connector(
    connector_id: str,
    db: Session = Depends(get_db)
):
    service = ConnectorService(db)
    if not service.delete_connector(connector_id):
        raise HTTPException(status_code=404, detail="Connector not found")
    return None
