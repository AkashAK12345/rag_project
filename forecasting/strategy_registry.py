"""
forecasting/strategy_registry.py

ForecastStrategyRegistry — central registry mapping ForecastMetric values
to their corresponding ForecastStrategy classes.

Mirrors the MetricRegistry pattern used by the Analytics Engine.

Usage:
    ForecastStrategyRegistry.register(ForecastMetric.SALES, SalesForecastStrategy)
    strategy_cls = ForecastStrategyRegistry.get(ForecastMetric.SALES)

Registration is performed at the bottom of each strategy module (import-time
side effect), keeping the registry and the strategy co-located without
introducing a separate configuration file.
"""

from typing import Type
from schemas.forecast_context import ForecastMetric
from forecasting.base_strategy import ForecastStrategy


class ForecastStrategyRegistry:
    """
    Central registry: ForecastMetric → ForecastStrategy class.

    Design: class-level dict so the registry is shared across all callers
    without requiring dependency injection. Consistent with MetricRegistry.
    """

    _registry: dict[ForecastMetric, Type[ForecastStrategy]] = {}

    @classmethod
    def register(
        cls,
        metric: ForecastMetric,
        strategy_class: Type[ForecastStrategy],
    ) -> None:
        """
        Register a strategy class for a given metric.

        Args:
            metric:         The ForecastMetric this strategy handles.
            strategy_class: The concrete ForecastStrategy subclass to register.
        """
        cls._registry[metric] = strategy_class

    @classmethod
    def get(cls, metric: ForecastMetric) -> Type[ForecastStrategy] | None:
        """
        Retrieve the registered strategy class for a metric.

        Args:
            metric: The ForecastMetric to look up.

        Returns:
            The ForecastStrategy subclass, or None if not registered.
        """
        return cls._registry.get(metric)

    @classmethod
    def deregister(cls, metric: ForecastMetric) -> None:
        """
        Remove the strategy registration for a given metric.

        Primarily used in tests to restore a clean registry state between
        test cases without relying on import-order side effects.

        Args:
            metric: The ForecastMetric to remove from the registry.
        """
        cls._registry.pop(metric, None)

    @classmethod
    def clear(cls) -> None:
        """
        Remove all registered strategies.

        Used in tests that need a completely empty registry to validate
        factory error handling without interference from other registrations.
        """
        cls._registry.clear()

    @classmethod
    def available_metrics(cls) -> list[ForecastMetric]:
        """Return a list of all metrics with a registered strategy."""
        return list(cls._registry.keys())
