"""
forecasting/strategy_factory.py

ForecastStrategyFactory — resolves and instantiates the correct ForecastStrategy
for a given ForecastMetric.

Mirrors MetricFactory. ForecastEngine is the only caller.

Phase 2 note:
    This factory is fully operational but the registry starts empty because
    no concrete strategy modules exist yet (they are introduced in Phase 3).
    Any attempt to create() an unregistered metric raises ValueError immediately
    so failures are loud and explicit rather than silently returning None.

    Concrete strategies (e.g. SalesForecastStrategy) register themselves at
    import time once Phase 3 is complete. The factory itself never needs to
    change — callers simply import the strategy module package and the registry
    is populated as a side effect.
"""

from schemas.forecast_context import ForecastMetric
from forecasting.base_strategy import ForecastStrategy
from forecasting.strategy_registry import ForecastStrategyRegistry

# ---------------------------------------------------------------------------
# Strategy modules are imported here to trigger self-registration.
# ---------------------------------------------------------------------------
import forecasting.strategies.sales_strategy               # noqa: F401
import forecasting.strategies.revenue_strategy             # noqa: F401
import forecasting.strategies.inventory_strategy           # noqa: F401
import forecasting.strategies.demand_strategy              # noqa: F401
import forecasting.strategies.expense_strategy             # noqa: F401
import forecasting.strategies.profit_strategy              # noqa: F401
import forecasting.strategies.branch_performance_strategy  # noqa: F401
import forecasting.strategies.purchase_strategy            # noqa: F401


class ForecastStrategyFactory:
    """
    Instantiates the appropriate ForecastStrategy for a given metric.

    ForecastEngine uses this factory exclusively — it never imports
    strategy classes directly.

    Resolution flow:
        ForecastStrategyFactory.create(metric)
            → ForecastStrategyRegistry.get(metric)
            → strategy_class()
            → ForecastStrategy (ready to call .forecast())
    """

    @staticmethod
    def create(metric: ForecastMetric) -> ForecastStrategy:
        """
        Instantiate the strategy registered for the given metric.

        Args:
            metric: A ForecastMetric enum value.

        Returns:
            An instantiated ForecastStrategy ready for use.

        Raises:
            ValueError: If no strategy is registered for the metric.
                        This is the expected error when strategy modules have
                        not been imported yet (Phase 2 state) or when an
                        unsupported metric is requested.
        """
        strategy_cls = ForecastStrategyRegistry.get(metric)
        if strategy_cls is None:
            available = [m.value for m in ForecastStrategyRegistry.available_metrics()]
            raise ValueError(
                f"No ForecastStrategy registered for metric '{metric.value}'. "
                f"Available: {available if available else 'none (no strategies registered yet)'}"
            )
        return strategy_cls()
