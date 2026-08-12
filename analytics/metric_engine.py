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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from schemas.dashboard import ChartSeries

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

        logger.debug(
            f"[DIAG] MetricEngine.compute() called with "
            f"{len(observations)} observation(s), "
            f"required_metrics={sorted(required)}"
        )

        # Group observations by domain
        obs_by_domain = defaultdict(list)
        for obs in observations:
            obs_by_domain[obs.domain].append(obs)

        computed_metrics: List[BusinessMetric] = []
        computed_charts: List['ChartSeries'] = []
        warnings: List[str] = []

        # Track which required metrics we have fulfilled
        fulfilled = set()

        # Execute calculators for all plan domains.
        # We iterate plan.domains (not just observed domains) so that
        # calculators with static/fallback chart data still run even when
        # the RAG index is empty and no observations were retrieved.
        domains_to_run = set(plan.domains)
        # Also include any domains that actually have observations
        domains_to_run.update(obs_by_domain.keys())

        for domain in domains_to_run:
            domain_obs = obs_by_domain.get(domain, [])
            calculators = MetricFactory.create(domain)
            if not calculators:
                logger.debug(f"MetricEngine: No calculators registered for domain {domain.value}")
                continue

            for calculator in calculators:
                # Pass the unresolved required metrics to the calculator
                pending_metrics = list(required - fulfilled)
                if not pending_metrics:
                    break  # All required metrics have been computed

                logger.debug(
                    f"[DIAG] MetricEngine: {calculator.__class__.__name__} "
                    f"domain={domain.value} obs={len(domain_obs)} "
                    f"pending={pending_metrics} fulfilled={sorted(fulfilled)}"
                )
                    
                try:
                    # The calculator will compute what it can and ignore what it can't
                    metrics = calculator.calculate(domain_obs, pending_metrics)
                    logger.debug(
                        f"[DIAG] MetricEngine: {calculator.__class__.__name__}.calculate() "
                        f"→ {len(metrics)} metric(s): {[m.metric_name for m in metrics]}"
                    )
                    for m in metrics:
                        cache_key = f"{m.metric_name}_{m.metric_value}_{m.calculated_from}"
                        if cache_key not in self._cache:
                            self._cache[cache_key] = m
                            computed_metrics.append(m)
                            # Normalize to snake_case to match the plan's required_metrics identifiers
                            fulfilled.add(m.metric_name.lower().replace(" ", "_"))
                            
                    charts = calculator.calculate_charts(domain_obs, pending_metrics)
                    logger.debug(
                        f"[DIAG] MetricEngine: {calculator.__class__.__name__}.calculate_charts() "
                        f"→ {len(charts)} chart(s): {[c.series_name for c in charts]}"
                    )
                    for c in charts:
                        # Assuming charts have a unique series_name
                        if not any(existing.series_name == c.series_name for existing in computed_charts):
                            computed_charts.append(c)
                            fulfilled.add(c.series_name.lower().replace(" ", "_"))
                            
                except Exception as e:
                    logger.error(f"MetricEngine: Calculator {calculator.__class__.__name__} failed: {e}", exc_info=True)
                    warnings.append(f"Calculation failed in {calculator.__class__.__name__}: {str(e)}")

        unfulfilled = required - fulfilled
        if unfulfilled:
            warnings.append(f"Could not compute the following requested metrics: {', '.join(unfulfilled)}")

        logger.info(
            f"MetricEngine: Computed {len(computed_metrics)} metrics, {len(computed_charts)} charts. "
            f"Fulfilled: {len(fulfilled)}/{len(required)} requested metrics."
        )
        logger.debug(
            f"[DIAG] MetricEngine: computed_metrics={[m.metric_name for m in computed_metrics]}, "
            f"computed_charts={[c.series_name for c in computed_charts]}"
        )
        if warnings:
            for w in warnings:
                logger.debug(f"[DIAG] MetricEngine warning: {w}")

        return AnalyticsContext(
            metrics=computed_metrics,
            charts=computed_charts,
            warnings=warnings
        )
