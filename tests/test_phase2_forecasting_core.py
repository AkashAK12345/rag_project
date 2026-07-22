"""
tests/test_phase2_forecasting_core.py

Phase 2 unit tests for the Forecasting Engine core infrastructure.

Covers:
  1. ForecastStrategy interface (ABC contract, concrete stub behaviour)
  2. ForecastStrategyRegistry (register, get, deregister, clear, available_metrics)
  3. ForecastStrategyFactory (resolution, instantiation, error on unregistered metric)
  4. AlgorithmSelector (select mapping for every ForecastMetric, compute stub contract)
  5. ForecastEngine (orchestration, warning collection, statelessness)

Design choices:
  - All tests use lightweight inline stub strategies so no algorithm
    or business-strategy modules are required (Phase 3 scope).
  - The registry is cleared in setUp/teardown fixtures to prevent
    cross-test contamination from the shared class-level dict.
  - ForecastEngine tests register stub strategies directly in the
    registry and remove them after each test.
"""

import pytest
from abc import ABC
from dataclasses import fields as dc_fields
from datetime import datetime, timezone
from typing import Type

from schemas.forecast_context import (
    ForecastAlgorithm,
    ForecastContext,
    ForecastHorizon,
    ForecastMetric,
    ForecastRequest,
    ForecastResult,
)
from forecasting.base_strategy import ForecastStrategy
from forecasting.strategy_registry import ForecastStrategyRegistry
from forecasting.strategy_factory import ForecastStrategyFactory
from forecasting.algorithm_selector import AlgorithmSelector
from forecasting.forecast_engine import ForecastEngine


# ---------------------------------------------------------------------------
# Helpers: stub implementations used across multiple test classes
# ---------------------------------------------------------------------------

def _make_result(metric: ForecastMetric, predicted: float = 100.0) -> ForecastResult:
    """Build a minimal but fully valid ForecastResult."""
    return ForecastResult(
        metric=metric,
        forecast_period=ForecastHorizon.MONTH.label,
        predicted_value=predicted,
        confidence=0.75,
        lower_bound=predicted * 0.9,
        upper_bound=predicted * 1.1,
        algorithm=ForecastAlgorithm.MOVING_AVERAGE,
        methodology="Stub (test only)",
        observations_used=5,
        historical_period="Last 5 observations",
    )


class StubSalesStrategy(ForecastStrategy):
    """Minimal concrete strategy for testing. Returns a fixed ForecastResult."""
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        return _make_result(request.metric, predicted=500.0)


class StubRevenueStrategy(ForecastStrategy):
    """Stub strategy for REVENUE metric."""
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        return _make_result(request.metric, predicted=1200.0)


class FailingStrategy(ForecastStrategy):
    """Strategy that raises ValueError to simulate insufficient-data scenarios."""
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        raise ValueError("Insufficient data: requires at least 3 observations.")


class UnexpectedErrorStrategy(ForecastStrategy):
    """Strategy that raises a generic exception."""
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        raise RuntimeError("Unexpected internal error in strategy.")


# ---------------------------------------------------------------------------
# Fixture: isolate the class-level registry for every test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_registry():
    """
    Clear the registry before and after every test in this module.

    This prevents registration side effects from one test contaminating
    another, regardless of test execution order.
    """
    ForecastStrategyRegistry.clear()
    yield
    ForecastStrategyRegistry.clear()


# ===========================================================================
# 1. ForecastStrategy interface
# ===========================================================================

class TestForecastStrategyInterface:
    """Verifies the ABC contract and concrete stub behaviour."""

    def test_is_abstract_base_class(self):
        assert issubclass(ForecastStrategy, ABC)

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError, match="abstract"):
            ForecastStrategy()  # type: ignore[abstract]

    def test_forecast_method_is_abstract(self):
        abstract_methods = getattr(ForecastStrategy, "__abstractmethods__", set())
        assert "forecast" in abstract_methods

    def test_concrete_stub_can_be_instantiated(self):
        strategy = StubSalesStrategy()
        assert isinstance(strategy, ForecastStrategy)

    def test_stub_forecast_returns_forecast_result(self):
        strategy = StubSalesStrategy()
        request = ForecastRequest(
            metric=ForecastMetric.SALES,
            forecast_horizon=ForecastHorizon.MONTH,
            observations=[],
        )
        result = strategy.forecast(request)
        assert isinstance(result, ForecastResult)

    def test_stub_forecast_result_has_correct_metric(self):
        strategy = StubSalesStrategy()
        request = ForecastRequest(
            metric=ForecastMetric.SALES,
            forecast_horizon=ForecastHorizon.MONTH,
            observations=[],
        )
        result = strategy.forecast(request)
        assert result.metric == ForecastMetric.SALES

    def test_stub_forecast_result_has_strongly_typed_algorithm(self):
        strategy = StubSalesStrategy()
        request = ForecastRequest(
            metric=ForecastMetric.SALES,
            forecast_horizon=ForecastHorizon.MONTH,
            observations=[],
        )
        result = strategy.forecast(request)
        assert isinstance(result.algorithm, ForecastAlgorithm)

    def test_incomplete_subclass_cannot_be_instantiated(self):
        class IncompleteStrategy(ForecastStrategy):
            pass  # forecast() not implemented

        with pytest.raises(TypeError, match="abstract"):
            IncompleteStrategy()  # type: ignore[abstract]

    def test_strategy_receives_all_request_fields(self):
        """Verify that the full ForecastRequest is accessible inside forecast()."""
        captured = {}

        class InspectingStrategy(ForecastStrategy):
            def forecast(self, request: ForecastRequest) -> ForecastResult:
                captured["metric"]   = request.metric
                captured["horizon"]  = request.forecast_horizon
                captured["obs"]      = request.observations
                return _make_result(request.metric)

        obs = ["obs1", "obs2"]
        request = ForecastRequest(
            metric=ForecastMetric.INVENTORY,
            forecast_horizon=ForecastHorizon.QUARTER,
            observations=obs,
        )
        InspectingStrategy().forecast(request)

        assert captured["metric"]  == ForecastMetric.INVENTORY
        assert captured["horizon"] == ForecastHorizon.QUARTER
        assert captured["obs"]     is obs


# ===========================================================================
# 2. ForecastStrategyRegistry
# ===========================================================================

class TestForecastStrategyRegistry:

    def test_empty_by_default_after_clear(self):
        assert ForecastStrategyRegistry.available_metrics() == []

    def test_register_and_get(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        retrieved = ForecastStrategyRegistry.get(ForecastMetric.SALES)
        assert retrieved is StubSalesStrategy

    def test_get_returns_none_for_unregistered_metric(self):
        result = ForecastStrategyRegistry.get(ForecastMetric.REVENUE)
        assert result is None

    def test_register_overwrites_existing(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubRevenueStrategy)
        retrieved = ForecastStrategyRegistry.get(ForecastMetric.SALES)
        assert retrieved is StubRevenueStrategy

    def test_multiple_metrics_registered_independently(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES,   StubSalesStrategy)
        ForecastStrategyRegistry.register(ForecastMetric.REVENUE, StubRevenueStrategy)
        assert ForecastStrategyRegistry.get(ForecastMetric.SALES)   is StubSalesStrategy
        assert ForecastStrategyRegistry.get(ForecastMetric.REVENUE) is StubRevenueStrategy

    def test_deregister_removes_entry(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        ForecastStrategyRegistry.deregister(ForecastMetric.SALES)
        assert ForecastStrategyRegistry.get(ForecastMetric.SALES) is None

    def test_deregister_nonexistent_is_silent(self):
        """deregister() on a metric that was never registered must not raise."""
        ForecastStrategyRegistry.deregister(ForecastMetric.PROFIT)  # should not raise

    def test_clear_removes_all_entries(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES,     StubSalesStrategy)
        ForecastStrategyRegistry.register(ForecastMetric.REVENUE,   StubRevenueStrategy)
        ForecastStrategyRegistry.clear()
        assert ForecastStrategyRegistry.available_metrics() == []

    def test_available_metrics_reflects_registrations(self):
        ForecastStrategyRegistry.register(ForecastMetric.DEMAND,   StubSalesStrategy)
        ForecastStrategyRegistry.register(ForecastMetric.EXPENSES, StubRevenueStrategy)
        metrics = ForecastStrategyRegistry.available_metrics()
        assert ForecastMetric.DEMAND   in metrics
        assert ForecastMetric.EXPENSES in metrics
        assert len(metrics) == 2

    def test_registry_stores_class_not_instance(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        retrieved = ForecastStrategyRegistry.get(ForecastMetric.SALES)
        # It should be the class itself, not an instance
        assert retrieved is StubSalesStrategy
        assert isinstance(retrieved, type)

    def test_registered_class_is_forecast_strategy_subclass(self):
        ForecastStrategyRegistry.register(ForecastMetric.PROFIT, StubSalesStrategy)
        retrieved = ForecastStrategyRegistry.get(ForecastMetric.PROFIT)
        assert issubclass(retrieved, ForecastStrategy)

    def test_registration_accepts_any_forecast_metric(self):
        """Every ForecastMetric value can be used as a registry key."""
        for metric in ForecastMetric:
            ForecastStrategyRegistry.register(metric, StubSalesStrategy)
        for metric in ForecastMetric:
            assert ForecastStrategyRegistry.get(metric) is StubSalesStrategy


# ===========================================================================
# 3. ForecastStrategyFactory
# ===========================================================================

class TestForecastStrategyFactory:

    def test_create_returns_instance_of_registered_class(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        instance = ForecastStrategyFactory.create(ForecastMetric.SALES)
        assert isinstance(instance, StubSalesStrategy)

    def test_create_returns_forecast_strategy(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        instance = ForecastStrategyFactory.create(ForecastMetric.SALES)
        assert isinstance(instance, ForecastStrategy)

    def test_create_raises_for_unregistered_metric(self):
        with pytest.raises(ValueError, match="No ForecastStrategy registered"):
            ForecastStrategyFactory.create(ForecastMetric.REVENUE)

    def test_error_message_contains_metric_name(self):
        with pytest.raises(ValueError, match="revenue"):
            ForecastStrategyFactory.create(ForecastMetric.REVENUE)

    def test_create_produces_new_instance_each_call(self):
        """Factory must not cache instances — each call returns a fresh object."""
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        instance1 = ForecastStrategyFactory.create(ForecastMetric.SALES)
        instance2 = ForecastStrategyFactory.create(ForecastMetric.SALES)
        assert instance1 is not instance2

    def test_create_all_registered_metrics(self):
        metrics_to_test = [
            ForecastMetric.SALES,
            ForecastMetric.REVENUE,
            ForecastMetric.INVENTORY,
        ]
        for metric in metrics_to_test:
            ForecastStrategyRegistry.register(metric, StubSalesStrategy)

        for metric in metrics_to_test:
            instance = ForecastStrategyFactory.create(metric)
            assert isinstance(instance, ForecastStrategy)

    def test_error_when_registry_empty(self):
        """With an empty registry all creates must raise ValueError."""
        for metric in ForecastMetric:
            with pytest.raises(ValueError):
                ForecastStrategyFactory.create(metric)


# ===========================================================================
# 4. AlgorithmSelector
# ===========================================================================

class TestAlgorithmSelector:

    # --- select() ---

    def test_select_returns_forecast_algorithm(self):
        for metric in ForecastMetric:
            result = AlgorithmSelector.select(metric)
            assert isinstance(result, ForecastAlgorithm)

    def test_select_all_metrics_have_mapping(self):
        """Every ForecastMetric must have an entry in the mapping."""
        for metric in ForecastMetric:
            # Must not raise
            algo = AlgorithmSelector.select(metric)
            assert algo is not None

    def test_select_specific_mappings(self):
        """Verify the documented metric→algorithm assignments."""
        assert AlgorithmSelector.select(ForecastMetric.SALES)              == ForecastAlgorithm.EXPONENTIAL_SMOOTHING
        assert AlgorithmSelector.select(ForecastMetric.REVENUE)            == ForecastAlgorithm.LINEAR_TREND
        assert AlgorithmSelector.select(ForecastMetric.INVENTORY)          == ForecastAlgorithm.WEIGHTED_MOVING_AVERAGE
        assert AlgorithmSelector.select(ForecastMetric.DEMAND)             == ForecastAlgorithm.EXPONENTIAL_SMOOTHING
        assert AlgorithmSelector.select(ForecastMetric.EXPENSES)           == ForecastAlgorithm.MOVING_AVERAGE
        assert AlgorithmSelector.select(ForecastMetric.PROFIT)             == ForecastAlgorithm.LINEAR_TREND
        assert AlgorithmSelector.select(ForecastMetric.BRANCH_PERFORMANCE) == ForecastAlgorithm.WEIGHTED_MOVING_AVERAGE
        assert AlgorithmSelector.select(ForecastMetric.PURCHASE)           == ForecastAlgorithm.MOVING_AVERAGE

    def test_select_mapping_covers_all_enum_members(self):
        """
        The mapping must cover every ForecastMetric member.
        This test will fail if a new ForecastMetric is added without
        a corresponding entry in _METRIC_ALGORITHM_MAP.
        """
        for metric in ForecastMetric:
            try:
                AlgorithmSelector.select(metric)
            except ValueError:
                pytest.fail(
                    f"ForecastMetric.{metric.name} has no algorithm mapping. "
                    f"Add it to _METRIC_ALGORITHM_MAP in algorithm_selector.py."
                )

    # --- compute() ---
    # Phase 2 tests for compute() raising NotImplementedError were removed
    # in Phase 3 once the algorithm modules were introduced.


# ===========================================================================
# 5. ForecastEngine
# ===========================================================================

class TestForecastEngine:

    def _engine(self) -> ForecastEngine:
        return ForecastEngine()

    def _request_obs(self):
        """Minimal observations list (contents irrelevant at Phase 2 level)."""
        return []

    # --- Instantiation ---

    def test_engine_can_be_instantiated(self):
        engine = self._engine()
        assert isinstance(engine, ForecastEngine)

    def test_engine_has_compute_method(self):
        assert callable(getattr(ForecastEngine, "compute", None))

    # --- Empty metric list ---

    def test_empty_metrics_returns_empty_context(self):
        engine = self._engine()
        ctx = engine.compute(
            observations=self._request_obs(),
            forecast_metrics=[],
            horizon=ForecastHorizon.MONTH,
        )
        assert isinstance(ctx, ForecastContext)
        assert ctx.results  == []
        assert ctx.warnings == []

    def test_empty_context_still_has_generated_at(self):
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[],
            horizon=ForecastHorizon.MONTH,
        )
        assert isinstance(ctx.generated_at, datetime)
        assert ctx.generated_at.tzinfo == timezone.utc

    # --- Successful forecasting ---

    def test_registered_metric_produces_result(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.MONTH,
        )
        assert len(ctx.results)  == 1
        assert len(ctx.warnings) == 0
        assert ctx.results[0].metric == ForecastMetric.SALES

    def test_multiple_registered_metrics_produce_multiple_results(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES,   StubSalesStrategy)
        ForecastStrategyRegistry.register(ForecastMetric.REVENUE, StubRevenueStrategy)
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES, ForecastMetric.REVENUE],
            horizon=ForecastHorizon.QUARTER,
        )
        assert len(ctx.results) == 2
        result_metrics = {r.metric for r in ctx.results}
        assert ForecastMetric.SALES   in result_metrics
        assert ForecastMetric.REVENUE in result_metrics

    def test_result_predicted_value_comes_from_strategy(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.MONTH,
        )
        # StubSalesStrategy returns predicted=500.0
        assert ctx.results[0].predicted_value == 500.0

    def test_horizon_is_passed_to_strategy(self):
        """Verify the horizon in ForecastRequest matches what the engine received."""
        captured_horizons = []

        class HorizonCapturingStrategy(ForecastStrategy):
            def forecast(self, request: ForecastRequest) -> ForecastResult:
                captured_horizons.append(request.forecast_horizon)
                return _make_result(request.metric)

        ForecastStrategyRegistry.register(ForecastMetric.SALES, HorizonCapturingStrategy)
        engine = self._engine()
        engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.YEAR,
        )
        assert captured_horizons == [ForecastHorizon.YEAR]

    def test_observations_are_passed_to_strategy(self):
        """Verify observations list is forwarded unchanged into ForecastRequest."""
        captured_obs = []

        class ObservationCapturingStrategy(ForecastStrategy):
            def forecast(self, request: ForecastRequest) -> ForecastResult:
                captured_obs.extend(request.observations)
                return _make_result(request.metric)

        obs_list = ["obs_a", "obs_b", "obs_c"]
        ForecastStrategyRegistry.register(ForecastMetric.DEMAND, ObservationCapturingStrategy)
        engine = self._engine()
        engine.compute(
            observations=obs_list,
            forecast_metrics=[ForecastMetric.DEMAND],
            horizon=ForecastHorizon.MONTH,
        )
        assert captured_obs == obs_list

    # --- Error handling / warnings ---

    def test_unregistered_metric_produces_warning_not_exception(self):
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.PROFIT],
            horizon=ForecastHorizon.MONTH,
        )
        assert ctx.results  == []
        assert len(ctx.warnings) == 1
        assert "profit" in ctx.warnings[0].lower()

    def test_strategy_value_error_produces_warning(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, FailingStrategy)
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.MONTH,
        )
        assert ctx.results  == []
        assert len(ctx.warnings) == 1

    def test_strategy_unexpected_error_produces_warning(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, UnexpectedErrorStrategy)
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.MONTH,
        )
        assert ctx.results  == []
        assert len(ctx.warnings) == 1

    def test_one_failing_metric_does_not_stop_others(self):
        """Engine continues processing remaining metrics after one failure."""
        ForecastStrategyRegistry.register(ForecastMetric.SALES,   FailingStrategy)
        ForecastStrategyRegistry.register(ForecastMetric.REVENUE, StubRevenueStrategy)
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES, ForecastMetric.REVENUE],
            horizon=ForecastHorizon.MONTH,
        )
        assert len(ctx.results)  == 1
        assert len(ctx.warnings) == 1
        assert ctx.results[0].metric == ForecastMetric.REVENUE

    def test_all_unregistered_metrics_all_warnings(self):
        engine = self._engine()
        ctx = engine.compute(
            observations=[],
            forecast_metrics=[
                ForecastMetric.SALES,
                ForecastMetric.REVENUE,
                ForecastMetric.PROFIT,
            ],
            horizon=ForecastHorizon.WEEK,
        )
        assert ctx.results  == []
        assert len(ctx.warnings) == 3

    # --- Statelessness ---

    def test_engine_is_stateless_across_calls(self):
        """
        Calling compute() twice on the same engine instance must produce
        independent results — no state leaks between calls.
        """
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        engine = self._engine()

        ctx1 = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.MONTH,
        )
        ctx2 = engine.compute(
            observations=[],
            forecast_metrics=[ForecastMetric.SALES],
            horizon=ForecastHorizon.QUARTER,
        )
        # Independent ForecastContext objects
        assert ctx1 is not ctx2
        assert ctx1.results is not ctx2.results

    def test_two_engine_instances_are_independent(self):
        """Two separately constructed ForecastEngine instances must behave identically."""
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        engine1 = ForecastEngine()
        engine2 = ForecastEngine()

        ctx1 = engine1.compute([], [ForecastMetric.SALES], ForecastHorizon.MONTH)
        ctx2 = engine2.compute([], [ForecastMetric.SALES], ForecastHorizon.MONTH)

        assert len(ctx1.results) == len(ctx2.results) == 1
        assert ctx1.results[0].predicted_value == ctx2.results[0].predicted_value

    # --- ForecastContext shape ---

    def test_returns_forecast_context(self):
        engine = self._engine()
        ctx = engine.compute([], [], ForecastHorizon.MONTH)
        assert isinstance(ctx, ForecastContext)

    def test_context_generated_at_is_utc(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        engine = self._engine()
        ctx = engine.compute([], [ForecastMetric.SALES], ForecastHorizon.MONTH)
        assert ctx.generated_at.tzinfo == timezone.utc

    def test_context_results_are_forecast_result_instances(self):
        ForecastStrategyRegistry.register(ForecastMetric.SALES, StubSalesStrategy)
        engine = self._engine()
        ctx = engine.compute([], [ForecastMetric.SALES], ForecastHorizon.MONTH)
        for result in ctx.results:
            assert isinstance(result, ForecastResult)
