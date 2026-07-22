from fastapi import APIRouter, Depends, Request
from schemas.system import HealthResponse, IndexStatsResponse, ModelConfigsResponse
from services.system_service import SystemService
from api.dependencies import get_rag_service, require_roles
from services.rag_service import RagService
from models.user import Role
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["System & Monitoring"])


def get_system_service(
    request: Request,
    rag_service: RagService = Depends(get_rag_service),
) -> SystemService:
    """Dependency to instantiate the SystemService with required application state."""
    start_time = getattr(request.app.state, "start_time", 0.0)
    return SystemService(rag_service=rag_service, start_time=start_time)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Public endpoint. Returns service health, uptime, and component readiness.",
    # No authentication required — needed by load balancers and Kubernetes probes
)
async def health_check(system_service: SystemService = Depends(get_system_service)):
    return system_service.get_health()


@router.get(
    "/index",
    response_model=IndexStatsResponse,
    summary="Index Storage Statistics",
    description="Returns statistics about the underlying vector index and tracked files. Requires ADMIN role.",
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
async def get_index_stats(system_service: SystemService = Depends(get_system_service)):
    logger.info("Handling request for /index statistics.")
    return system_service.get_index_stats()


@router.get(
    "/models",
    response_model=ModelConfigsResponse,
    summary="Active Model Configurations",
    description="Returns active LLM, embedding model, and vector store details. Requires ADMIN role.",
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
async def get_models(system_service: SystemService = Depends(get_system_service)):
    logger.info("Handling request for /models configuration.")
    return system_service.get_model_configs()
