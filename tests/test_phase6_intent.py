import pytest
from services.intent_service import RuleBasedIntentAnalyzer
from schemas.forecast_context import ForecastMetric, ForecastHorizon
from schemas.retrieval_plan import QueryIntent, QueryType

@pytest.fixture
def analyzer():
    return RuleBasedIntentAnalyzer()

def test_non_forecast_query(analyzer):
    plan = analyzer.analyze("summarize sales for last week")
    assert not plan.forecast_metrics
    assert plan.forecast_horizon is None
    assert plan.intent == QueryIntent.IDENTIFY_TREND
    assert plan.query_type == QueryType.TREND

def test_single_forecast_metric_default_horizon(analyzer):
    plan = analyzer.analyze("forecast sales")
    assert plan.forecast_metrics == [ForecastMetric.SALES]
    assert plan.forecast_horizon is None
    # Existing intent is preserved (fallback to general/lookup or whatever matched)
    # the exact intent doesn't matter as much as ensuring forecast fields are populated
    # without introducing QueryType.FORECAST.

def test_multiple_forecast_metrics(analyzer):
    plan = analyzer.analyze("predict revenue and profit")
    assert set(plan.forecast_metrics) == {ForecastMetric.REVENUE, ForecastMetric.PROFIT}
    assert plan.forecast_horizon is None

def test_explicit_horizon_week(analyzer):
    plan = analyzer.analyze("estimate inventory next week")
    assert plan.forecast_metrics == [ForecastMetric.INVENTORY]
    assert plan.forecast_horizon == ForecastHorizon.WEEK

def test_explicit_horizon_month(analyzer):
    plan = analyzer.analyze("forecast sales next month")
    assert plan.forecast_metrics == [ForecastMetric.SALES]
    assert plan.forecast_horizon == ForecastHorizon.MONTH

def test_explicit_horizon_quarter(analyzer):
    plan = analyzer.analyze("predict revenue for next quarter")
    assert plan.forecast_metrics == [ForecastMetric.REVENUE]
    assert plan.forecast_horizon == ForecastHorizon.QUARTER

def test_explicit_horizon_year(analyzer):
    plan = analyzer.analyze("forecast sales and profit next year")
    assert set(plan.forecast_metrics) == {ForecastMetric.SALES, ForecastMetric.PROFIT}
    assert plan.forecast_horizon == ForecastHorizon.YEAR

def test_mixed_analytics_and_forecast(analyzer):
    # E.g. summarize past performance and predict future
    plan = analyzer.analyze("summarize recent sales and forecast next month")
    assert plan.intent == QueryIntent.IDENTIFY_TREND
    assert plan.query_type == QueryType.TREND
    assert plan.forecast_metrics == [ForecastMetric.SALES]
    assert plan.forecast_horizon == ForecastHorizon.MONTH
