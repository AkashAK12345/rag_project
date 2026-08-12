"""
forecasting/strategies/demand_strategy.py
"""

from schemas.forecast_context import ForecastMetric, ForecastRequest, ForecastResult
from forecasting.base_strategy import ForecastStrategy
from forecasting.algorithm_selector import AlgorithmSelector
from forecasting.strategy_registry import ForecastStrategyRegistry
from forecasting.strategies._helpers import extract_numeric_series, build_result

class DemandForecastStrategy(ForecastStrategy):
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        from schemas.dashboard import ChartSeries, ForecastPoint
        from schemas.forecast_context import ForecastAlgorithm

        series = extract_numeric_series(request.observations, ["demand_volume", "quantity_demanded", "demand"])

        if len(series) < 3:
            raise ValueError("Requires at least 3 numeric observations for Demand forecast.")

        algo = AlgorithmSelector.select(request.metric)
        predicted, lower, upper, methodology = AlgorithmSelector.compute(
            algo, series, request.forecast_horizon.days
        )

        # Build mock timeline data
        timeline_data = [
            ForecastPoint(date="Mar", actual=1200),
            ForecastPoint(date="Apr", actual=1350),
            ForecastPoint(date="May", actual=1420),
            ForecastPoint(date="Jun", actual=1500, forecast=1500),
            ForecastPoint(date="Jul", forecast=predicted * 0.95, lower_bound=lower * 0.95, upper_bound=upper * 0.95),
            ForecastPoint(date="Aug", forecast=predicted, lower_bound=lower, upper_bound=upper),
        ]

        timeline = ChartSeries(series_name="demand_forecast", data=timeline_data)

        return build_result(
            request.metric, request.forecast_horizon, predicted, lower, upper, methodology, algo, len(series), timeline
        )

# Self-register at import time
ForecastStrategyRegistry.register(ForecastMetric.DEMAND, DemandForecastStrategy)
