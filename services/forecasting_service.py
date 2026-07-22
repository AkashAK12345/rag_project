"""
services/forecasting_service.py

ForecastingService — thin service wrapper around the stateless ForecastEngine.

Mirrors AnalyticsService in structure and lifecycle:
  - ForecastEngine is shared (constructed once, reused across all requests).
  - This service reads forecast_metrics and forecast_horizon from the RetrievalPlan.
  - It applies the application default horizon when the plan does not specify one.
  - The rest of the pipeline (QueryService, RagService) never instantiates
    ForecastEngine or ForecastStrategyFactory directly.

Default horizon:
  ForecastHorizon.MONTH (30 days). This default will be made configurable
  via FORECAST_DEFAULT_HORIZON in .env in a future configuration milestone.
"""

from core.logging import get_logger
from schemas.forecast_context import ForecastContext, ForecastHorizon
from schemas.query_context import BusinessObservation
from schemas.retrieval_plan import RetrievalPlan
from forecasting.forecast_engine import ForecastEngine

logger = get_logger(__name__)

# Application default when the user did not specify a horizon.
# Future: read from config / .env
_DEFAULT_HORIZON = ForecastHorizon.MONTH


class ForecastingService:
    """
    Coordinates deterministic forecasting.

    A single ForecastEngine instance is created at service construction time
    and reused for every request (the engine is stateless).
    """

    def __init__(self) -> None:
        self._engine = ForecastEngine()

    def compute(
        self,
        observations: list[BusinessObservation],
        plan: RetrievalPlan,
    ) -> ForecastContext:
        """
        Compute forecasts for the metrics requested in the plan.

        Args:
            observations: All BusinessObservations extracted by BusinessContextBuilder.
            plan:         The RetrievalPlan carrying forecast_metrics and forecast_horizon.

        Returns:
            A ForecastContext with structured ForecastResults and any warnings.
            If plan.forecast_metrics is empty, returns an empty ForecastContext immediately.
        """
        if not plan.forecast_metrics:
            logger.debug("ForecastingService: no forecast_metrics in plan. Skipping.")
            return ForecastContext()

        horizon = plan.forecast_horizon or _DEFAULT_HORIZON
        if plan.forecast_horizon is None:
            logger.info(
                f"ForecastingService: no horizon specified; "
                f"using default '{_DEFAULT_HORIZON.value}'."
            )

        logger.info(
            f"ForecastingService: computing {len(plan.forecast_metrics)} forecast(s) "
            f"from {len(observations)} observation(s), horizon='{horizon.value}'."
        )

        context = self._engine.compute(
            observations=observations,
            forecast_metrics=plan.forecast_metrics,
            horizon=horizon,
        )

        logger.info(
            f"ForecastingService: complete — "
            f"{len(context.results)} result(s), {len(context.warnings)} warning(s), "
            f"generated_at={context.generated_at.isoformat()}."
        )

        return context
