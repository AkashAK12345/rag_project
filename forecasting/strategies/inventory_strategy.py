"""
forecasting/strategies/inventory_strategy.py
"""

from schemas.forecast_context import ForecastMetric, ForecastRequest, ForecastResult
from forecasting.base_strategy import ForecastStrategy
from forecasting.algorithm_selector import AlgorithmSelector
from forecasting.strategy_registry import ForecastStrategyRegistry
from forecasting.strategies._helpers import extract_numeric_series, build_result

class InventoryForecastStrategy(ForecastStrategy):
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        from schemas.dashboard import ChartSeries, ForecastPoint
        from schemas.forecast_context import ForecastAlgorithm

        series = extract_numeric_series(request.observations, ["inventory_level", "stock_count", "inventory"])

        if len(series) < 3:
            raise ValueError("Requires at least 3 numeric observations for Inventory forecast.")

        algo = AlgorithmSelector.select(request.metric)
        predicted, lower, upper, methodology = AlgorithmSelector.compute(
            algo, series, request.forecast_horizon.days
        )

        # Build mock timeline data
        timeline_data = [
            ForecastPoint(date="Mar", actual=500),
            ForecastPoint(date="Apr", actual=450),
            ForecastPoint(date="May", actual=480),
            ForecastPoint(date="Jun", actual=420, forecast=420),
            ForecastPoint(date="Jul", forecast=predicted * 1.05, lower_bound=lower * 1.05, upper_bound=upper * 1.05),
            ForecastPoint(date="Aug", forecast=predicted, lower_bound=lower, upper_bound=upper),
        ]

        timeline = ChartSeries(series_name="inventory_forecast", data=timeline_data)

        return build_result(
            request.metric, request.forecast_horizon, predicted, lower, upper, methodology, algo, len(series), timeline
        )

# Self-register at import time
ForecastStrategyRegistry.register(ForecastMetric.INVENTORY, InventoryForecastStrategy)
