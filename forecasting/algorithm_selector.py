"""
forecasting/algorithm_selector.py

AlgorithmSelector — the central authority for metric-to-algorithm assignment.

Design decision: algorithm selection is deliberately separated from the
ForecastStrategy implementations. This means:

  1. Strategies do NOT hardcode which algorithm they use.
  2. Changing the algorithm for any metric requires editing a single mapping
     here — not hunting across multiple strategy files.
  3. Future ML algorithms (Prophet, ARIMA, XGBoost) can be swapped in
     per-metric without touching strategy or service code.

Strategies call both methods:
  1. select() to determine which algorithm applies.
  2. compute() to execute the chosen algorithm.

This keeps strategies thin — they own observation extraction; AlgorithmSelector
owns algorithm dispatch.
"""

from schemas.forecast_context import ForecastAlgorithm, ForecastMetric
from forecasting.algorithms import (
    moving_average,
    weighted_moving_average,
    exponential_smoothing,
    linear_trend,
)


# ---------------------------------------------------------------------------
# Metric → Algorithm mapping
# ---------------------------------------------------------------------------
# Each entry maps a ForecastMetric to its preferred default algorithm.
# Override at any time without touching strategy implementations.
#
# Rationale for each choice:
#   SALES              → Exponential Smoothing: reactive to level shifts in sales data
#   REVENUE            → Linear Trend:          revenue tends to follow directional growth
#   INVENTORY          → Weighted MA:           recency bias suits inventory fluctuations
#   DEMAND             → Exponential Smoothing: demand reacts quickly; ES tracks well
#   EXPENSES           → Moving Average:        expenses are stable; simple avg reliable
#   PROFIT             → Linear Trend:          profit trajectories are directional
#   BRANCH_PERFORMANCE → Weighted MA:           branch data needs recency weight
#   PURCHASE           → Moving Average:        procurement cycles are regular

_METRIC_ALGORITHM_MAP: dict[ForecastMetric, ForecastAlgorithm] = {
    ForecastMetric.SALES:              ForecastAlgorithm.EXPONENTIAL_SMOOTHING,
    ForecastMetric.REVENUE:            ForecastAlgorithm.LINEAR_TREND,
    ForecastMetric.INVENTORY:          ForecastAlgorithm.WEIGHTED_MOVING_AVERAGE,
    ForecastMetric.DEMAND:             ForecastAlgorithm.EXPONENTIAL_SMOOTHING,
    ForecastMetric.EXPENSES:           ForecastAlgorithm.MOVING_AVERAGE,
    ForecastMetric.PROFIT:             ForecastAlgorithm.LINEAR_TREND,
    ForecastMetric.BRANCH_PERFORMANCE: ForecastAlgorithm.WEIGHTED_MOVING_AVERAGE,
    ForecastMetric.PURCHASE:           ForecastAlgorithm.MOVING_AVERAGE,
}


# ---------------------------------------------------------------------------
# AlgorithmSelector
# ---------------------------------------------------------------------------

class AlgorithmSelector:
    """
    Resolves which algorithm to use for a given metric and dispatches computation.

    All methods are static — this class carries no instance state.
    """

    @staticmethod
    def select(metric: ForecastMetric) -> ForecastAlgorithm:
        """
        Return the default ForecastAlgorithm for the given metric.

        Args:
            metric: A ForecastMetric enum value.

        Returns:
            The appropriate ForecastAlgorithm.

        Raises:
            ValueError: If the metric has no registered algorithm.
                        This is a programming error — every ForecastMetric
                        must have an entry in _METRIC_ALGORITHM_MAP.
        """
        algorithm = _METRIC_ALGORITHM_MAP.get(metric)
        if algorithm is None:
            raise ValueError(
                f"No algorithm registered for ForecastMetric.{metric.name}. "
                f"Add it to _METRIC_ALGORITHM_MAP in forecasting/algorithm_selector.py."
            )
        return algorithm

    @staticmethod
    def compute(
        algorithm: ForecastAlgorithm,
        values: list[float],
        horizon_days: int,
        **kwargs,
    ) -> tuple[float, float, float, str]:
        """
        Dispatch to the correct algorithm module and return the result.

        Args:
            algorithm:    The ForecastAlgorithm to execute.
            values:       Ordered list of historical floats (oldest → newest).
            horizon_days: The forecast horizon in days.
            **kwargs:     Algorithm-specific overrides (e.g. alpha, window).

        Returns:
            (predicted_value, lower_bound, upper_bound, methodology_label)

        Raises:
            ValueError: If the algorithm is not supported.
        """
        if algorithm == ForecastAlgorithm.MOVING_AVERAGE:
            return moving_average.compute(values, horizon_days, **kwargs)
            
        if algorithm == ForecastAlgorithm.WEIGHTED_MOVING_AVERAGE:
            return weighted_moving_average.compute(values, horizon_days, **kwargs)
            
        if algorithm == ForecastAlgorithm.EXPONENTIAL_SMOOTHING:
            return exponential_smoothing.compute(values, horizon_days, **kwargs)
            
        if algorithm == ForecastAlgorithm.LINEAR_TREND:
            return linear_trend.compute(values, horizon_days)
            
        raise ValueError(
            f"AlgorithmSelector.compute() unhandled algorithm "
            f"'{algorithm.value}'."
        )
