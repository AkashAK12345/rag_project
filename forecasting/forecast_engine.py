"""
forecasting/forecast_engine.py

ForecastEngine — stateless orchestrator for the Forecasting Engine.

Responsibilities:
  - Receive a list of ForecastMetrics, a ForecastHorizon, and historical
    BusinessObservations.
  - Construct one ForecastRequest per requested metric.
  - Delegate to ForecastStrategyFactory to resolve the correct strategy.
  - Collect ForecastResults and aggregate warnings.
  - Return a ForecastContext.

Design rules:
  - STATELESS. Carries no per-request data.
  - NEVER calls the LLM.
  - NEVER reads files or accesses the vector store.
  - NEVER knows about the user's question or RetrievalPlan internals.
  - If a metric cannot be resolved (no strategy) or produces an error,
    the failure is captured as a warning and excluded from results —
    remaining metrics continue processing.
"""

from core.logging import get_logger
from schemas.forecast_context import (
    ForecastContext,
    ForecastHorizon,
    ForecastMetric,
    ForecastRequest,
)
from schemas.query_context import BusinessObservation
from forecasting.strategy_factory import ForecastStrategyFactory

logger = get_logger(__name__)


class ForecastEngine:
    """
    Stateless forecasting orchestrator.

    ForecastingService holds one shared instance and calls compute() per request.
    This class carries no mutable state — it is safe to reuse across concurrent
    requests (assuming strategy implementations are also stateless, which they are).
    """

    def compute(
        self,
        observations: list[BusinessObservation],
        forecast_metrics: list[ForecastMetric],
        horizon: ForecastHorizon,
    ) -> ForecastContext:
        """
        Produce a ForecastContext for the requested metrics.

        Args:
            observations:     Historical BusinessObservations from the retrieved context.
            forecast_metrics: The metrics to forecast (from RetrievalPlan.forecast_metrics).
            horizon:          The requested forecast time window.

        Returns:
            ForecastContext with one ForecastResult per successfully forecasted metric,
            plus any warnings for metrics that could not be processed.
        """
        results = []
        warnings = []

        logger.info(
            f"ForecastEngine: computing {len(forecast_metrics)} metric(s) "
            f"from {len(observations)} observation(s) "
            f"over horizon '{horizon.value}'."
        )

        for metric in forecast_metrics:
            try:
                strategy = ForecastStrategyFactory.create(metric)
            except ValueError as e:
                warning = f"Metric '{metric.value}': {e}"
                logger.warning(f"ForecastEngine: {warning}")
                warnings.append(warning)
                continue

            request = ForecastRequest(
                metric=metric,
                forecast_horizon=horizon,
                observations=observations,
            )

            try:
                result = strategy.forecast(request)
                results.append(result)
                logger.info(
                    f"ForecastEngine: [{metric.value}] predicted={result.predicted_value}, "
                    f"confidence={result.confidence:.3f}, "
                    f"algorithm={result.algorithm.value}, "
                    f"observations_used={result.observations_used}"
                )
            except ValueError as e:
                # Typically: insufficient data points for this metric
                warning = f"Metric '{metric.value}': {e}"
                logger.warning(f"ForecastEngine: {warning}")
                warnings.append(warning)
            except Exception as e:
                warning = f"Metric '{metric.value}': unexpected error — {e}"
                logger.error(f"ForecastEngine: {warning}", exc_info=True)
                warnings.append(warning)

        logger.info(
            f"ForecastEngine: complete — "
            f"{len(results)} result(s), {len(warnings)} warning(s)."
        )

        return ForecastContext(results=results, warnings=warnings)
