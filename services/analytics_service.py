"""
services/analytics_service.py

Exposes the Business Analytics Engine to the QueryService.
"""

from typing import List

from core.logging import get_logger
from schemas.query_context import BusinessObservation
from schemas.retrieval_plan import RetrievalPlan
from schemas.analytics_context import AnalyticsContext
from analytics.metric_engine import MetricEngine


logger = get_logger(__name__)


class AnalyticsService:
    """
    Coordinates deterministic metric calculation.
    Instantiates a MetricEngine per request to leverage request-scoped caching.
    """

    def compute(self, observations: List[BusinessObservation], plan: RetrievalPlan) -> AnalyticsContext:
        """
        Compute required metrics deterministically from business observations.
        
        Args:
            observations: List of BusinessObservations from retrieved nodes.
            plan: The RetrievalPlan that specifies which metrics are required.
            
        Returns:
            An AnalyticsContext populated with computed BusinessMetrics.
        """
        logger.info(f"AnalyticsService: Computing metrics for {len(observations)} observations.")
        
        # Instantiate a fresh engine per request so the memoization cache is request-scoped
        engine = MetricEngine()
        
        # Run calculations
        context = engine.compute(observations, plan)
        
        logger.info(
            f"AnalyticsService: Computation complete. "
            f"Generated {len(context.metrics)} metrics."
        )
        
        return context
