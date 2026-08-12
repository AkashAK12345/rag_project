"""
tests/test_phase1_schemas.py

Phase 1 schema verification tests for the Forecasting Engine.

These tests verify:
  - All enum members are present with correct string values.
  - ForecastHorizon.label and ForecastHorizon.days properties are correct.
  - ForecastRequest, ForecastResult, ForecastContext are correctly structured.
  - RetrievalPlan carries the two new forecasting fields with correct defaults.
  - ForecastContext.generated_at is auto-populated as a UTC datetime.
  - ForecastResult requires all mandatory fields (no silent defaults on provenance).
  - All schema types are plain dataclasses (no Pydantic/FastAPI dependency).

No business logic, algorithms, or strategies are imported or tested here.
"""

import pytest
from dataclasses import fields as dc_fields
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Import all Phase 1 schema types
# ---------------------------------------------------------------------------
from schemas.forecast_context import (
    ForecastMetric,
    ForecastAlgorithm,
    ForecastHorizon,
    ForecastRequest,
    ForecastResult,
    ForecastContext,
)
from schemas.retrieval_plan import RetrievalPlan, QueryType, QueryIntent
from schemas.report import BusinessDomain, ReportType


# ===========================================================================
# ForecastMetric
# ===========================================================================

class TestForecastMetric:
    def test_all_required_members_present(self):
        required = {
            "SALES", "REVENUE", "INVENTORY", "DEMAND",
            "EXPENSES", "PROFIT", "BRANCH_PERFORMANCE", "PURCHASE",
        }
        actual = {m.name for m in ForecastMetric}
        assert required == actual, f"Missing or extra members: {required.symmetric_difference(actual)}"

    def test_values_are_snake_case_strings(self):
        for m in ForecastMetric:
            assert isinstance(m.value, str)
            assert m.value == m.value.lower(), f"{m.name} value should be lowercase"

    def test_is_str_enum(self):
        """ForecastMetric values should compare equal to plain strings."""
        assert ForecastMetric.SALES == "sales"
        assert ForecastMetric.BRANCH_PERFORMANCE == "branch_performance"

    def test_all_specific_values(self):
        assert ForecastMetric.SALES.value              == "sales"
        assert ForecastMetric.REVENUE.value            == "revenue"
        assert ForecastMetric.INVENTORY.value          == "inventory"
        assert ForecastMetric.DEMAND.value             == "demand"
        assert ForecastMetric.EXPENSES.value           == "expenses"
        assert ForecastMetric.PROFIT.value             == "profit"
        assert ForecastMetric.BRANCH_PERFORMANCE.value == "branch_performance"
        assert ForecastMetric.PURCHASE.value           == "purchase"


# ===========================================================================
# ForecastAlgorithm
# ===========================================================================

class TestForecastAlgorithm:
    def test_all_required_members_present(self):
        required = {
            "MOVING_AVERAGE",
            "WEIGHTED_MOVING_AVERAGE",
            "EXPONENTIAL_SMOOTHING",
            "LINEAR_TREND",
        }
        actual = {m.name for m in ForecastAlgorithm}
        assert required == actual

    def test_values_are_snake_case_strings(self):
        for m in ForecastAlgorithm:
            assert isinstance(m.value, str)
            assert m.value == m.value.lower()

    def test_is_str_enum(self):
        assert ForecastAlgorithm.MOVING_AVERAGE          == "moving_average"
        assert ForecastAlgorithm.WEIGHTED_MOVING_AVERAGE == "weighted_moving_average"
        assert ForecastAlgorithm.EXPONENTIAL_SMOOTHING   == "exponential_smoothing"
        assert ForecastAlgorithm.LINEAR_TREND            == "linear_trend"


# ===========================================================================
# ForecastHorizon
# ===========================================================================

class TestForecastHorizon:
    def test_all_required_members_present(self):
        required = {"WEEK", "MONTH", "QUARTER", "YEAR"}
        actual = {m.name for m in ForecastHorizon}
        assert required == actual

    def test_values(self):
        assert ForecastHorizon.WEEK.value    == "next_week"
        assert ForecastHorizon.MONTH.value   == "next_month"
        assert ForecastHorizon.QUARTER.value == "next_quarter"
        assert ForecastHorizon.YEAR.value    == "next_year"

    def test_is_str_enum(self):
        assert ForecastHorizon.MONTH == "next_month"

    def test_label_property(self):
        assert ForecastHorizon.WEEK.label    == "Next 7 Days"
        assert ForecastHorizon.MONTH.label   == "Next 30 Days"
        assert ForecastHorizon.QUARTER.label == "Next 90 Days"
        assert ForecastHorizon.YEAR.label    == "Next 365 Days"

    def test_days_property(self):
        assert ForecastHorizon.WEEK.days    == 7
        assert ForecastHorizon.MONTH.days   == 30
        assert ForecastHorizon.QUARTER.days == 90
        assert ForecastHorizon.YEAR.days    == 365


# ===========================================================================
# ForecastRequest
# ===========================================================================

class TestForecastRequest:
    def _make(self, **overrides):
        defaults = dict(
            metric=ForecastMetric.SALES,
            forecast_horizon=ForecastHorizon.MONTH,
            observations=[],
        )
        defaults.update(overrides)
        return ForecastRequest(**defaults)

    def test_instantiation(self):
        req = self._make()
        assert req.metric           == ForecastMetric.SALES
        assert req.forecast_horizon == ForecastHorizon.MONTH
        assert req.observations     == []

    def test_required_fields_present(self):
        field_names = {f.name for f in dc_fields(ForecastRequest)}
        assert "metric"           in field_names
        assert "forecast_horizon" in field_names
        assert "observations"     in field_names

    def test_all_metrics_accepted(self):
        for metric in ForecastMetric:
            req = self._make(metric=metric)
            assert req.metric == metric

    def test_all_horizons_accepted(self):
        for horizon in ForecastHorizon:
            req = self._make(forecast_horizon=horizon)
            assert req.forecast_horizon == horizon

    def test_observations_accepts_list(self):
        """observations is typed as list to avoid circular import; accepts any list."""
        req = self._make(observations=["a", "b", "c"])
        assert len(req.observations) == 3


# ===========================================================================
# ForecastResult
# ===========================================================================

class TestForecastResult:
    def _make(self, **overrides):
        defaults = dict(
            metric=ForecastMetric.REVENUE,
            forecast_period="Next 30 Days",
            predicted_value=12500.0,
            confidence=0.82,
            lower_bound=11000.0,
            upper_bound=14000.0,
            algorithm=ForecastAlgorithm.LINEAR_TREND,
            methodology="Linear Trend Regression (slope=2.50, n=12)",
            observations_used=12,
            historical_period="Last 12 observations",
        )
        defaults.update(overrides)
        return ForecastResult(**defaults)

    def test_instantiation(self):
        r = self._make()
        assert r.metric            == ForecastMetric.REVENUE
        assert r.forecast_period   == "Next 30 Days"
        assert r.predicted_value   == 12500.0
        assert r.confidence        == 0.82
        assert r.lower_bound       == 11000.0
        assert r.upper_bound       == 14000.0
        assert r.algorithm         == ForecastAlgorithm.LINEAR_TREND
        assert r.methodology       == "Linear Trend Regression (slope=2.50, n=12)"
        assert r.observations_used == 12
        assert r.historical_period == "Last 12 observations"

    def test_all_eleven_fields_required(self):
        """All ForecastResult fields must be explicitly provided — no silent defaults."""
        field_names = {f.name for f in dc_fields(ForecastResult)}
        expected = {
            "metric", "forecast_period", "predicted_value", "confidence",
            "lower_bound", "upper_bound", "algorithm", "methodology",
            "observations_used", "historical_period", "timeline",
        }
        assert expected == field_names, (
            f"Field mismatch. Extra: {field_names - expected}. Missing: {expected - field_names}"
        )

    def test_metric_is_strongly_typed(self):
        r = self._make(metric=ForecastMetric.INVENTORY)
        assert isinstance(r.metric, ForecastMetric)

    def test_algorithm_is_strongly_typed(self):
        r = self._make(algorithm=ForecastAlgorithm.EXPONENTIAL_SMOOTHING)
        assert isinstance(r.algorithm, ForecastAlgorithm)

    def test_all_metric_algorithm_combinations(self):
        """Smoke test: all ForecastMetric × ForecastAlgorithm combinations accepted."""
        for metric in ForecastMetric:
            for algo in ForecastAlgorithm:
                r = self._make(metric=metric, algorithm=algo)
                assert r.metric    == metric
                assert r.algorithm == algo


# ===========================================================================
# ForecastContext
# ===========================================================================

class TestForecastContext:
    def _make_result(self):
        return ForecastResult(
            metric=ForecastMetric.SALES,
            forecast_period="Next 7 Days",
            predicted_value=5000.0,
            confidence=0.75,
            lower_bound=4200.0,
            upper_bound=5800.0,
            algorithm=ForecastAlgorithm.EXPONENTIAL_SMOOTHING,
            methodology="Exponential Smoothing (a=0.30)",
            observations_used=6,
            historical_period="Last 6 observations",
        )

    def test_default_instantiation(self):
        ctx = ForecastContext()
        assert ctx.results   == []
        assert ctx.warnings  == []
        assert ctx.generated_at is not None

    def test_generated_at_is_utc_datetime(self):
        ctx = ForecastContext()
        assert isinstance(ctx.generated_at, datetime)
        assert ctx.generated_at.tzinfo == timezone.utc

    def test_generated_at_is_recent(self):
        before = datetime.now(timezone.utc)
        ctx = ForecastContext()
        after  = datetime.now(timezone.utc)
        assert before <= ctx.generated_at <= after

    def test_each_instance_gets_unique_timestamp(self):
        ctx1 = ForecastContext()
        ctx2 = ForecastContext()
        # Both should be valid datetimes; not necessarily different in fast tests,
        # but should not share the same object reference.
        assert ctx1.generated_at is not ctx2.generated_at

    def test_results_populated(self):
        r = self._make_result()
        ctx = ForecastContext(results=[r])
        assert len(ctx.results) == 1
        assert ctx.results[0].metric == ForecastMetric.SALES

    def test_warnings_populated(self):
        ctx = ForecastContext(warnings=["Insufficient data for DEMAND metric."])
        assert len(ctx.warnings) == 1
        assert "DEMAND" in ctx.warnings[0]

    def test_field_names(self):
        field_names = {f.name for f in dc_fields(ForecastContext)}
        assert field_names == {"results", "warnings", "generated_at"}

    def test_no_prompt_strings(self):
        """ForecastContext must NOT contain any text/prompt fields."""
        field_names = {f.name for f in dc_fields(ForecastContext)}
        for forbidden in ("text", "forecast_text", "prompt", "summary"):
            assert forbidden not in field_names, (
                f"ForecastContext must not contain a '{forbidden}' field "
                "(prompt assembly belongs in RagService)."
            )


# ===========================================================================
# RetrievalPlan — new forecasting fields
# ===========================================================================

class TestRetrievalPlanForecastFields:
    def _make_plan(self, **overrides):
        defaults = dict(
            query_type=QueryType.SUMMARIZE,
            intent=QueryIntent.SUMMARIZE_REPORT,
            domains=[BusinessDomain.SALES],
        )
        defaults.update(overrides)
        return RetrievalPlan(**defaults)

    def test_forecast_metrics_defaults_to_empty_list(self):
        plan = self._make_plan()
        assert plan.forecast_metrics == []

    def test_forecast_horizon_defaults_to_none(self):
        plan = self._make_plan()
        assert plan.forecast_horizon is None

    def test_forecast_metrics_accepts_list_of_enum(self):
        plan = self._make_plan(
            forecast_metrics=[ForecastMetric.SALES, ForecastMetric.REVENUE]
        )
        assert len(plan.forecast_metrics) == 2
        assert ForecastMetric.SALES   in plan.forecast_metrics
        assert ForecastMetric.REVENUE in plan.forecast_metrics

    def test_forecast_horizon_accepts_enum_value(self):
        for horizon in ForecastHorizon:
            plan = self._make_plan(forecast_horizon=horizon)
            assert plan.forecast_horizon == horizon

    def test_existing_fields_unchanged(self):
        """None of the pre-existing RetrievalPlan fields should be removed or renamed."""
        plan = self._make_plan()
        field_names = {f.name for f in dc_fields(RetrievalPlan)}
        for expected in (
            "query_type", "intent", "domains", "report_types",
            "top_k", "confidence", "time_range", "required_metrics", "metadata_hints",
        ):
            assert expected in field_names, f"Pre-existing field '{expected}' is missing."

    def test_query_type_unchanged(self):
        """QueryType enum must still contain its original 8 members."""
        expected = {
            "LOOKUP", "SUMMARIZE", "COMPARE", "TREND",
            "ANOMALY", "RECOMMENDATION", "EXPLAIN", "ROOT_CAUSE",
        }
        assert {m.name for m in QueryType} == expected

    def test_query_intent_unchanged(self):
        """QueryIntent enum must still contain its original 11 members."""
        expected = {
            "LOOKUP_VALUE", "SUMMARIZE_REPORT", "COMPARE_ENTITIES",
            "IDENTIFY_TOP_PERFORMER", "IDENTIFY_BOTTOM_PERFORMER",
            "IDENTIFY_TREND", "IDENTIFY_ANOMALY", "REQUEST_RECOMMENDATION",
            "EXPLAIN_CAUSE", "ROOT_CAUSE_ANALYSIS", "GENERAL",
        }
        assert {m.name for m in QueryIntent} == expected

    def test_no_forecast_querytype_added(self):
        """No FORECAST member should be present in QueryType."""
        assert not hasattr(QueryType, "FORECAST"), (
            "QueryType.FORECAST must not be added — forecasting is a capability flag, "
            "not a query type."
        )

    def test_no_forecast_queryintent_added(self):
        """No REQUEST_FORECAST member should be present in QueryIntent."""
        assert not hasattr(QueryIntent, "REQUEST_FORECAST"), (
            "QueryIntent.REQUEST_FORECAST must not be added."
        )

    def test_forecast_metrics_is_independent_of_required_metrics(self):
        """forecast_metrics and required_metrics are distinct fields with different purposes."""
        plan = self._make_plan(
            required_metrics=["Total Revenue"],
            forecast_metrics=[ForecastMetric.REVENUE],
        )
        assert plan.required_metrics  == ["Total Revenue"]
        assert plan.forecast_metrics  == [ForecastMetric.REVENUE]
