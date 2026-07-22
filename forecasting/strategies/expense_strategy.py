"""
forecasting/strategies/expense_strategy.py
"""

from schemas.forecast_context import ForecastMetric, ForecastRequest, ForecastResult
from forecasting.base_strategy import ForecastStrategy
from forecasting.algorithm_selector import AlgorithmSelector
from forecasting.strategy_registry import ForecastStrategyRegistry
from forecasting.strategies._helpers import extract_numeric_series, build_result

class ExpenseForecastStrategy(ForecastStrategy):
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        series = extract_numeric_series(request.observations, ["total_expenses", "expenses", "costs"])
        if len(series) < 3:
            raise ValueError(f"Requires at least 3 numeric observations, found {len(series)}")
            
        algo = AlgorithmSelector.select(request.metric)
        predicted, lower, upper, methodology = AlgorithmSelector.compute(
            algo, series, request.forecast_horizon.days
        )
        
        return build_result(
            request.metric, request.forecast_horizon, predicted, lower, upper, methodology, algo, len(series)
        )

# Self-register at import time
ForecastStrategyRegistry.register(ForecastMetric.EXPENSES, ExpenseForecastStrategy)
