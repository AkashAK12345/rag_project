"""
analytics/metric_engine.py

Core engine that processes BusinessObservations through registered Calculators.
Implements request-scoped memoization to avoid recalculating identical metrics.
"""

from typing import List, Dict, Set
from collections import defaultdict

from core.logging import get_logger
from schemas.query_context import BusinessObservation
from schemas.retrieval_plan import RetrievalPlan
from schemas.business_metric import BusinessMetric
from schemas.analytics_context import AnalyticsContext
from analytics.metric_factory import MetricFactory

logger = get_logger(__name__)


class MetricEngine:
    """
    Deterministically computes analytics for a given request.
    Instantiated once per request by the AnalyticsService to provide request-scoped caching.
    """

    def __init__(self):
        # Cache computed metrics to avoid recalculation within the same request
        self._cache: Dict[str, BusinessMetric] = {}

    def compute(self, observations: List[BusinessObservation], plan: RetrievalPlan) -> AnalyticsContext:
        """
        Process observations and compute the metrics requested in the plan.
        
        Args:
            observations: List of all factual observations extracted by IngestionService.
            plan: The RetrievalPlan containing `required_metrics`.
            
        Returns:
            AnalyticsContext with computed BusinessMetrics.
        """
        required = set(plan.required_metrics)
        if not required:
            logger.info("MetricEngine: No metrics requested in RetrievalPlan. Skipping computation.")
            return AnalyticsContext()

        # Group observations by domain
        obs_by_domain = defaultdict(list)
        for obs in observations:
            obs_by_domain[obs.domain].append(obs)

        computed_metrics: List[BusinessMetric] = []
        warnings: List[str] = []

        # Track which required metrics we have fulfilled
        fulfilled = set()

        # Execute calculators for each domain that has observations
        for domain, domain_obs in obs_by_domain.items():
            calculators = MetricFactory.create(domain)
            if not calculators:
                logger.debug(f"MetricEngine: No calculators registered for domain {domain.value}")
                continue

            for calculator in calculators:
                # Pass the unresolved required metrics to the calculator
                pending_metrics = list(required - fulfilled)
                if not pending_metrics:
                    break  # All required metrics have been computed
                    
                try:
                    # The calculator will compute what it can and ignore what it can't
                    metrics = calculator.calculate(domain_obs, pending_metrics)
                    for m in metrics:
                        cache_key = f"{m.metric_name}_{m.metric_value}_{m.calculated_from}"
                        if cache_key not in self._cache:
                            self._cache[cache_key] = m
                            computed_metrics.append(m)
                            fulfilled.add(m.metric_name.lower())
                except Exception as e:
                    logger.error(f"MetricEngine: Calculator {calculator.__class__.__name__} failed: {e}", exc_info=True)
                    warnings.append(f"Calculation failed in {calculator.__class__.__name__}: {str(e)}")

        unfulfilled = required - fulfilled
        if unfulfilled:
            warnings.append(f"Could not compute the following requested metrics: {', '.join(unfulfilled)}")

        logger.info(
            f"MetricEngine: Computed {len(computed_metrics)} metrics. "
            f"Fulfilled: {len(fulfilled)}/{len(required)} requested metrics."
        )

        return AnalyticsContext(
            metrics=computed_metrics,
            warnings=warnings
        )
