from fastapi import APIRouter, Depends, HTTPException, status
from schemas.report import WorkbookCapabilityGraph
from services.capability_service import CapabilityService, CapabilityExplanation
from api.dependencies import require_roles
from models.user import Role
from schemas.report import BusinessDomain

router = APIRouter(prefix="/workbooks", tags=["Capabilities"])


@router.get(
    "/{workbook_id}/capabilities",
    response_model=WorkbookCapabilityGraph,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.ANALYST))]
)
def get_capabilities(workbook_id: str):
    """Returns the complete WorkbookCapabilityGraph for debugging and explainability."""
    service = CapabilityService()
    graph = service.repository.load(workbook_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Capabilities not found for this workbook.")
    return graph


@router.get(
    "/{workbook_id}/capabilities/explain",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.ANALYST))]
)
def explain_capability(
    workbook_id: str,
    metric: str | None = None,
    chart: str | None = None
):
    """Explains why a specific metric or chart is supported or unsupported."""
    if not metric and not chart:
        raise HTTPException(status_code=400, detail="Must provide either 'metric' or 'chart' parameter.")
        
    service = CapabilityService()
    # Ensure the workbook actually exists
    graph = service.repository.load(workbook_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Capabilities not found for this workbook.")
        
    explanation: CapabilityExplanation | None = None
    if metric:
        explanation = service.explain_metric(metric, BusinessDomain.UNKNOWN)
    elif chart:
        explanation = service.explain_chart(chart, BusinessDomain.UNKNOWN)
        
    return explanation
