import pytest
from unittest.mock import MagicMock

from schemas.query_context import BusinessObservation
from schemas.retrieval_plan import RetrievalPlan, QueryType, QueryIntent
from schemas.report import BusinessDomain
from schemas.forecast_context import (
    ForecastMetric,
    ForecastHorizon,
    ForecastContext,
    ForecastResult,
    ForecastAlgorithm
)
from services.forecasting_service import ForecastingService

@pytest.fixture
def service():
    return ForecastingService()

def make_plan(**kwargs):
    defaults = dict(
        query_type=QueryType.SUMMARIZE,
        intent=QueryIntent.SUMMARIZE_REPORT,
        domains=[BusinessDomain.SALES],
    )
    defaults.update(kwargs)
    return RetrievalPlan(**defaults)

def test_no_forecast_requested(service):
    # plan with empty forecast_metrics
    plan = make_plan()
    assert plan.forecast_metrics == []
    
    # Mock engine.compute to ensure it's NEVER called
    service._engine.compute = MagicMock()
    
    context = service.compute(observations=[], plan=plan)
    
    assert isinstance(context, ForecastContext)
    assert context.results == []
    assert context.warnings == []
    service._engine.compute.assert_not_called()

def test_single_metric_with_default_horizon(service):
    plan = make_plan(forecast_metrics=[ForecastMetric.SALES], forecast_horizon=None)
    observations = []
    
    mock_context = ForecastContext(results=[MagicMock()])
    service._engine.compute = MagicMock(return_value=mock_context)
    
    context = service.compute(observations, plan)
    
    assert context is mock_context
    service._engine.compute.assert_called_once_with(
        observations=observations,
        forecast_metrics=[ForecastMetric.SALES],
        horizon=ForecastHorizon.MONTH  # The default
    )

def test_multiple_metrics(service):
    plan = make_plan(
        forecast_metrics=[ForecastMetric.SALES, ForecastMetric.REVENUE],
        forecast_horizon=None
    )
    
    service._engine.compute = MagicMock(return_value=ForecastContext())
    
    service.compute([], plan)
    
    service._engine.compute.assert_called_once_with(
        observations=[],
        forecast_metrics=[ForecastMetric.SALES, ForecastMetric.REVENUE],
        horizon=ForecastHorizon.MONTH
    )

def test_explicit_horizon(service):
    plan = make_plan(
        forecast_metrics=[ForecastMetric.INVENTORY],
        forecast_horizon=ForecastHorizon.YEAR
    )
    
    service._engine.compute = MagicMock(return_value=ForecastContext())
    
    service.compute([], plan)
    
    service._engine.compute.assert_called_once_with(
        observations=[],
        forecast_metrics=[ForecastMetric.INVENTORY],
        horizon=ForecastHorizon.YEAR
    )

def test_exception_handling_in_engine_surfaces(service):
    # The service itself does not catch engine exceptions; the engine handles strategy exceptions,
    # but if the engine itself crashes, the service should let it bubble up, or we just verify
    # how the service delegates it.
    plan = make_plan(forecast_metrics=[ForecastMetric.SALES])
    
    service._engine.compute = MagicMock(side_effect=RuntimeError("Engine failure"))
    
    with pytest.raises(RuntimeError, match="Engine failure"):
        service.compute([], plan)
