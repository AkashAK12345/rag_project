"""
services/analytics_dashboard_service.py

Orchestration service for the Analytics Dashboard.
Retrieves observations and delegates exclusively to the MetricEngine for business logic.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
import json

from core.logging import get_logger
from services.retrieval_service import RetrievalService
from services.context_builder import BusinessContextBuilder
from analytics.metric_engine import MetricEngine
from schemas.retrieval_plan import RetrievalPlan, QueryType, QueryIntent
from schemas.report import BusinessDomain
from schemas.dashboard import (
    AnalyticsDashboardResponse,
    AnalyticsDashboardOverview,
    AnalyticsDashboardCharts,
    AnalyticsDashboardInsights,
    ChartSeries
)

logger = get_logger(__name__)

class AnalyticsDashboardService:
    """
    Orchestrates data fetching and engine invocation for the Analytics Dashboard.
    Strictly NO business logic (calculations) in this class.
    """

    def __init__(self, rag_service):
        self._retrieval_service = RetrievalService(index=rag_service.index)
        self._context_builder = BusinessContextBuilder()

    def get_dashboard(self) -> AnalyticsDashboardResponse:
        """
        Builds the Analytics Dashboard Response.
        """
        # 1. Define the metrics we need the engine to calculate
        plan = RetrievalPlan(
            query_type=QueryType.SUMMARIZE,
            intent=QueryIntent.GENERAL,
            domains=[
                BusinessDomain.FINANCE, 
                BusinessDomain.SALES, 
                BusinessDomain.INVENTORY, 
                BusinessDomain.EMPLOYEES
            ],
            required_metrics=[
                "total_revenue",
                "active_branches",
                "total_orders",
                "avg_order_value",
                "revenue_growth_pct",
                "revenue_trend",
                "top_products",
                "sales_by_category",
                "branch_performance",
                "inventory_status"
            ],
            top_k=100  # Pull a large context for comprehensive dashboard view
        )

        # 2. Retrieve observations
        logger.debug(
            f"[DIAG] AnalyticsDashboardService: RetrievalPlan.required_metrics={plan.required_metrics}, "
            f"domains={[d.value for d in plan.domains]}, top_k={plan.top_k}"
        )
        nodes = self._retrieval_service.retrieve("Get all data for analytics dashboard", plan)
        business_context = self._context_builder.build(nodes, plan)
        
        all_observations = []
        for section in business_context.sections:
            all_observations.extend(section.observations)

        logger.debug(
            f"[DIAG] AnalyticsDashboardService: retrieved {len(nodes)} node(s), "
            f"{len(all_observations)} observation(s) across "
            f"{len(business_context.sections)} domain section(s)."
        )
        for section in business_context.sections:
            logger.debug(
                f"[DIAG]   domain={section.domain.value}, "
                f"docs={section.document_count}, "
                f"obs={len(section.observations)}"
            )

        if len(all_observations) == 0:
            logger.debug("[DIAG] AnalyticsDashboardService: zero observations — falling back to demo data.")
            from services.analytics_demo_data import get_analytics_demo_data
            return get_analytics_demo_data()

        # 3. Consult CapabilityService
        from services.capability_service import CapabilityService
        from schemas.dashboard import KpiValue, CapabilityStatus
        
        cap_service = CapabilityService()
        
        # 4. Compute deterministically using the engine
        engine = MetricEngine()
        analytics_context = engine.compute(all_observations, plan)

        metrics_map = {
            m.metric_name.lower().replace(" ", "_"): m.metric_value
            for m in analytics_context.metrics
        }
        charts_map = {c.series_name: c for c in analytics_context.charts}
        
        def get_kpi_value(name: str, default_val: Any, val_type: type) -> KpiValue:
            exp = cap_service.explain_metric(name, BusinessDomain.UNKNOWN)
            val = val_type(metrics_map.get(name, default_val))
            
            # If it's supported but we didn't compute anything or it's empty, we could set status = empty
            # but the engine will return 0 if no data matched.
            status = exp.status
            if status == "supported" and val == default_val and not metrics_map.get(name):
                status = "empty"
                
            cap = CapabilityStatus(status=status, reason=exp.reason, required_fields=exp.required_fields)
            return KpiValue(value=val, capability=cap)
            
        def get_chart_series(name: str) -> ChartSeries:
            exp = cap_service.explain_chart(name, BusinessDomain.UNKNOWN)
            series = charts_map.get(name, ChartSeries(series_name=name, data=[]))
            
            status = exp.status
            if status == "supported" and not series.data:
                status = "empty"
                
            series.capability = CapabilityStatus(status=status, reason=exp.reason, required_fields=exp.required_fields)
            return series

        overview = AnalyticsDashboardOverview(
            total_revenue=get_kpi_value("total_revenue", 0.0, float),
            active_branches=get_kpi_value("active_branches", 0, int),
            total_orders=get_kpi_value("total_orders", 0, int),
            avg_order_value=get_kpi_value("avg_order_value", 0.0, float),
            revenue_growth_pct=KpiValue(
                value=0.0,
                capability=CapabilityStatus(
                    status="unsupported",
                    reason="Not implemented by current deterministic engine."
                )
            )
        )

        charts = AnalyticsDashboardCharts(
            revenueTrend=get_chart_series("revenue_trend"),
            topProducts=get_chart_series("top_products"),
            salesByCategory=ChartSeries(
                series_name="sales_by_category",
                data=[],
                capability=CapabilityStatus(
                    status="unsupported",
                    reason="Not implemented by current deterministic engine."
                )
            ),
            branchPerformance=get_chart_series("branch_performance"),
            inventoryStatus=get_chart_series("inventory_status")
        )

        insights = AnalyticsDashboardInsights(
            summary="Analytics generated deterministically.",
            generatedAt=datetime.now(timezone.utc)
        )

        response = AnalyticsDashboardResponse(
            overview=overview,
            charts=charts,
            insights=insights
        )
        return response

