"""
forecasting/strategies/revenue_strategy.py
"""

from schemas.forecast_context import ForecastMetric, ForecastRequest, ForecastResult
from forecasting.base_strategy import ForecastStrategy
from forecasting.algorithm_selector import AlgorithmSelector
from forecasting.strategy_registry import ForecastStrategyRegistry
from forecasting.strategies._helpers import extract_numeric_series, build_result

class RevenueForecastStrategy(ForecastStrategy):
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        from schemas.dashboard import ChartSeries, ForecastPoint
        from forecasting.strategies._helpers import derive_confidence
        from schemas.forecast_context import ForecastAlgorithm

        series = extract_numeric_series(request.observations, ["total_revenue", "revenue", "revenue_amount"])

        if len(series) < 3:
            raise ValueError("Requires at least 3 numeric observations for Revenue forecast.")

        algo = AlgorithmSelector.select(request.metric)
        predicted, lower, upper, methodology = AlgorithmSelector.compute(
            algo, series, request.forecast_horizon.days
        )

        # Build mock timeline data
        # In reality, this would use historical timestamps and forecast model extrapolation
        timeline_data = [
            ForecastPoint(date="Mar", actual=55000),
            ForecastPoint(date="Apr", actual=58000),
            ForecastPoint(date="May", actual=62000),
            ForecastPoint(date="Jun", actual=60000, forecast=60000),
            ForecastPoint(date="Jul", forecast=predicted * 0.9, lower_bound=lower * 0.9, upper_bound=upper * 0.9),
            ForecastPoint(date="Aug", forecast=predicted, lower_bound=lower, upper_bound=upper),
        ]

        timeline = ChartSeries(series_name="revenue_forecast", data=timeline_data)

        return build_result(
            request.metric, request.forecast_horizon, predicted, lower, upper, methodology, algo, len(series), timeline
        )

# Self-register at import time
ForecastStrategyRegistry.register(ForecastMetric.REVENUE, RevenueForecastStrategy)
