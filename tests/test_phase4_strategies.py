import pytest

from schemas.query_context import BusinessObservation
from schemas.report import BusinessDomain
from schemas.forecast_context import (
    ForecastMetric,
    ForecastHorizon,
    ForecastRequest,
    ForecastResult,
)
from forecasting.strategy_factory import ForecastStrategyFactory
from forecasting.strategy_registry import ForecastStrategyRegistry

def make_obs(kv: dict) -> BusinessObservation:
    return BusinessObservation(
        domain=BusinessDomain.SALES,
        report_type="test",
        source_file="test.csv",
        sheet="Sheet1",
        key_values=kv,
        raw_text="Test obs",
        relevance_score=1.0,
    )

def test_registry_registration():
    # Make sure all 8 strategies are registered
    metrics = ForecastStrategyRegistry.available_metrics()
    assert len(metrics) == 8
    assert set(metrics) == set(ForecastMetric)

def test_successful_extraction():
    strategy = ForecastStrategyFactory.create(ForecastMetric.SALES)
    obs = [
        make_obs({"total_sales": "100"}),
        make_obs({"total_sales": "110"}),
        make_obs({"total_sales": "120"}),
    ]
    req = ForecastRequest(ForecastMetric.SALES, ForecastHorizon.MONTH, obs)
    result = strategy.forecast(req)
    assert isinstance(result, ForecastResult)
    assert result.metric == ForecastMetric.SALES
    assert result.predicted_value > 0

def test_missing_business_fields():
    strategy = ForecastStrategyFactory.create(ForecastMetric.REVENUE)
    # Give it observations that have no revenue-related fields
    obs = [
        make_obs({"foo": "100"}),
        make_obs({"bar": "110"}),
        make_obs({"baz": "120"}),
    ]
    req = ForecastRequest(ForecastMetric.REVENUE, ForecastHorizon.MONTH, obs)
    with pytest.raises(ValueError, match="Requires at least 3"):
        strategy.forecast(req)

def test_insufficient_history():
    strategy = ForecastStrategyFactory.create(ForecastMetric.INVENTORY)
    obs = [
        make_obs({"inventory_level": "100"}),
        make_obs({"inventory_level": "110"}),
    ]
    req = ForecastRequest(ForecastMetric.INVENTORY, ForecastHorizon.MONTH, obs)
    with pytest.raises(ValueError, match="Requires at least 3"):
        strategy.forecast(req)

def test_invalid_observations():
    strategy = ForecastStrategyFactory.create(ForecastMetric.DEMAND)
    # Valid fields but invalid values
    obs = [
        make_obs({"demand": "abc"}),
        make_obs({"demand": "def"}),
        make_obs({"demand": "ghi"}),
    ]
    req = ForecastRequest(ForecastMetric.DEMAND, ForecastHorizon.MONTH, obs)
    with pytest.raises(ValueError, match="Requires at least 3"):
        strategy.forecast(req)
        
def test_valid_with_junk_ignored():
    strategy = ForecastStrategyFactory.create(ForecastMetric.DEMAND)
    obs = [
        make_obs({"demand": "10"}),
        make_obs({"demand": "abc"}),  # this one is skipped
        make_obs({"demand": "20"}),
        make_obs({"demand": "30"}),
    ]
    req = ForecastRequest(ForecastMetric.DEMAND, ForecastHorizon.MONTH, obs)
    result = strategy.forecast(req)
    assert result.observations_used == 3

def test_result_construction():
    strategy = ForecastStrategyFactory.create(ForecastMetric.EXPENSES)
    obs = [
        make_obs({"expenses": "100"}),
        make_obs({"expenses": "110"}),
        make_obs({"expenses": "120"}),
        make_obs({"expenses": "130"}),
    ]
    req = ForecastRequest(ForecastMetric.EXPENSES, ForecastHorizon.WEEK, obs)
    result = strategy.forecast(req)
    assert result.metric == ForecastMetric.EXPENSES
    assert result.forecast_period == ForecastHorizon.WEEK.label
    assert "Moving Average" in result.methodology
    assert result.observations_used == 4
    assert "Last 4" in result.historical_period
