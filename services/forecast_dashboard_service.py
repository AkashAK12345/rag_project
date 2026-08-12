"""
services/forecast_dashboard_service.py

Orchestration service for the Forecast Dashboard.
Retrieves observations and delegates exclusively to the ForecastEngine for business logic.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone

from core.logging import get_logger
from services.retrieval_service import RetrievalService
from services.context_builder import BusinessContextBuilder
from forecasting.forecast_engine import ForecastEngine
from schemas.retrieval_plan import RetrievalPlan, QueryType, QueryIntent
from schemas.report import BusinessDomain
from schemas.forecast_context import ForecastMetric, ForecastHorizon
from schemas.dashboard import (
    ForecastDashboardResponse,
    ForecastDashboardOverview,
    ForecastDashboardCharts,
    ForecastDashboardInsights,
    ChartSeries
)

logger = get_logger(__name__)

class ForecastDashboardService:
    """
    Orchestrates data fetching and engine invocation for the Forecast Dashboard.
    Strictly NO business logic (calculations) in this class.
    """

    def __init__(self, rag_service):
        self._retrieval_service = RetrievalService(index=rag_service.index)
        self._context_builder = BusinessContextBuilder()
        self._engine = ForecastEngine()

    def get_dashboard(self, horizon: str = "next_month") -> ForecastDashboardResponse:
        """
        Builds the Forecast Dashboard Response.
        """
        # Map string to enum
        try:
            forecast_horizon = ForecastHorizon(horizon)
        except ValueError:
            forecast_horizon = ForecastHorizon.MONTH

        # 1. Define the metrics we need the engine to calculate
        plan = RetrievalPlan(
            query_type=QueryType.SUMMARIZE,
            intent=QueryIntent.GENERAL,
            domains=[
                BusinessDomain.FINANCE, 
                BusinessDomain.INVENTORY, 
                BusinessDomain.SALES,
                BusinessDomain.EMPLOYEES
            ],
            forecast_metrics=[
                ForecastMetric.REVENUE,
                ForecastMetric.DEMAND,
                ForecastMetric.INVENTORY
            ],
            forecast_horizon=forecast_horizon,
            top_k=100
        )

        # 2. Retrieve observations
        logger.debug(
            f"[DIAG] ForecastDashboardService: forecast_metrics={[m.value for m in plan.forecast_metrics]}, "
            f"horizon={forecast_horizon.value}, top_k={plan.top_k}"
        )
        nodes = self._retrieval_service.retrieve("Get all data for forecasting", plan)
        business_context = self._context_builder.build(nodes, plan)
        
        all_observations = []
        for section in business_context.sections:
            all_observations.extend(section.observations)

        logger.debug(
            f"[DIAG] ForecastDashboardService: retrieved {len(nodes)} node(s), "
            f"{len(all_observations)} observation(s) across "
            f"{len(business_context.sections)} domain section(s)."
        )

        if len(all_observations) == 0:
            logger.debug("[DIAG] ForecastDashboardService: zero observations — falling back to demo data.")
            from services.forecast_demo_data import get_forecast_demo_data
            return get_forecast_demo_data()

        # 3. Validate capabilities via CapabilityService
        from services.capability_service import CapabilityService
        cap_service = CapabilityService()
        
        missing_capabilities = []
        for f_metric in plan.forecast_metrics:
            # Map forecast metric to standard metric name
            metric_mapping = {
                ForecastMetric.REVENUE: "total_revenue",
                ForecastMetric.DEMAND: "total_orders",
                ForecastMetric.INVENTORY: "total_stock"
            }
            mapped_name = metric_mapping.get(f_metric, f_metric.value)
            
            exp = cap_service.explain_metric(mapped_name, BusinessDomain.UNKNOWN)
            if exp.status != "supported":
                missing_capabilities.append({
                    "unsupported_forecast": f_metric.value,
                    "missing_capability": mapped_name,
                    "missing_required_fields": exp.required_fields,
                    "reason": exp.reason
                })
                
        if missing_capabilities:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Forecast unsupported due to missing data capabilities.",
                    "missing_capabilities": missing_capabilities
                }
            )

        # 4. Compute deterministically using the engine
        forecast_context = self._engine.compute(all_observations, plan.forecast_metrics, plan.forecast_horizon)

        logger.debug(
            f"[DIAG] ForecastDashboardService: engine returned "
            f"{len(forecast_context.results)} result(s), "
            f"{len(forecast_context.warnings)} warning(s)."
        )
        for r in forecast_context.results:
            logger.debug(
                f"[DIAG]   metric={r.metric.value}, "
                f"predicted_value={r.predicted_value}, "
                f"confidence={r.confidence:.3f}, "
                f"observations_used={r.observations_used}"
            )

        # 4. Map the engine's flat results to the structured DTO
        results_map = {r.metric.value: r for r in forecast_context.results}

        # Safe extraction for overview KPIs
        # Assume predicted_value represents the overview number
        rev_forecast = results_map.get(ForecastMetric.REVENUE.value)
        demand_forecast = results_map.get(ForecastMetric.DEMAND.value)
        inv_forecast = results_map.get(ForecastMetric.INVENTORY.value)

        overview = ForecastDashboardOverview(
            projected_revenue_30d=rev_forecast.predicted_value if rev_forecast else 0.0,
            expected_demand_growth_pct=demand_forecast.predicted_value if demand_forecast else 0.0,
            inventory_risk_items=int(inv_forecast.predicted_value) if inv_forecast else 0
        )

        # Safe extraction for charts (assumes timelines are populated)
        charts = ForecastDashboardCharts(
            revenueForecast=rev_forecast.timeline if (rev_forecast and rev_forecast.timeline) else ChartSeries(series_name="revenue_forecast", data=[]),
            demandForecast=demand_forecast.timeline if (demand_forecast and demand_forecast.timeline) else ChartSeries(series_name="demand_forecast", data=[]),
            inventoryForecast=inv_forecast.timeline if (inv_forecast and inv_forecast.timeline) else ChartSeries(series_name="inventory_forecast", data=[])
        )
        
        # Calculate overall confidence
        confidences = [r.confidence for r in forecast_context.results if r.confidence > 0]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 1.0

        insights = ForecastDashboardInsights(
            summary="Forecast generated deterministically.",
            confidence=overall_confidence
        )

        response = ForecastDashboardResponse(
            overview=overview,
            charts=charts,
            insights=insights
        )
        logger.debug(
            f"[DIAG] ForecastDashboardResponse final DTO: "
            f"projected_revenue_30d={response.overview.projected_revenue_30d}, "
            f"expected_demand_growth_pct={response.overview.expected_demand_growth_pct}, "
            f"inventory_risk_items={response.overview.inventory_risk_items}, "
            f"confidence={response.insights.confidence:.3f}"
        )
        return response
