from fastapi import APIRouter, Depends
from schemas.dashboard import AnalyticsDashboardResponse
from services.analytics_dashboard_service import AnalyticsDashboardService
from api.dependencies import get_rag_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(rag_service = Depends(get_rag_service)):
    """
    Retrieve the deterministically computed analytics dashboard data.
    """
    service = AnalyticsDashboardService(rag_service)
    return service.get_dashboard()

