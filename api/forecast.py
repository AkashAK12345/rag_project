from fastapi import APIRouter, Depends, Query
from schemas.dashboard import ForecastDashboardResponse
from services.forecast_dashboard_service import ForecastDashboardService
from api.dependencies import get_rag_service

router = APIRouter(prefix="/forecast", tags=["Forecast"])

@router.get("/dashboard", response_model=ForecastDashboardResponse)
async def get_forecast_dashboard(
    horizon: str = Query("next_month", description="The forecast horizon (e.g. next_week, next_month, next_quarter)"),
    rag_service = Depends(get_rag_service)
):
    """
    Retrieve the deterministically computed forecast dashboard data.
    """
    service = ForecastDashboardService(rag_service)
    return service.get_dashboard(horizon=horizon)
