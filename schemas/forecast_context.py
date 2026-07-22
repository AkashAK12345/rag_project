"""
schemas/forecast_context.py

Data contracts for the Forecasting Engine.

Design decision: plain dataclasses (not Pydantic) — same philosophy as
AnalyticsContext and ReasoningContext. These objects flow through the
in-process pipeline only and are never serialised directly to the API.

ForecastMetric     — strongly-typed canonical metric identifiers
ForecastAlgorithm  — machine-readable algorithm identifiers
ForecastHorizon    — supported forecast time windows
ForecastRequest    — input to ForecastEngine (metric + horizon + observations)
ForecastResult     — single deterministic forecast with full provenance
ForecastContext    — aggregate output consumed by RagService
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.query_context import BusinessObservation


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ForecastMetric(str, Enum):
    """
    Canonical, strongly-typed identifiers for every forecastable business metric.

    Using an enum instead of plain strings ensures:
      - Typos are caught at import/startup time.
      - Strategy registry keys are always valid.
      - API clients receive a documented set of valid values.
    """
    SALES              = "sales"
    REVENUE            = "revenue"
    INVENTORY          = "inventory"
    DEMAND             = "demand"
    EXPENSES           = "expenses"
    PROFIT             = "profit"
    BRANCH_PERFORMANCE = "branch_performance"
    PURCHASE           = "purchase"


class ForecastAlgorithm(str, Enum):
    """
    Machine-readable algorithm identifier written into every ForecastResult.

    Enables downstream consumers (dashboards, agents, tests) to inspect which
    algorithm produced a result without parsing the human-readable methodology string.
    """
    MOVING_AVERAGE          = "moving_average"
    WEIGHTED_MOVING_AVERAGE = "weighted_moving_average"
    EXPONENTIAL_SMOOTHING   = "exponential_smoothing"
    LINEAR_TREND            = "linear_trend"


class ForecastHorizon(str, Enum):
    """
    Supported forecast time windows.

    ForecastEngine maps each value to a day-count used by algorithms.
    Adding a new horizon (e.g. HALF_YEAR) requires only adding an entry
    here and updating the mapping in ForecastEngine.
    """
    WEEK    = "next_week"      # 7 days
    MONTH   = "next_month"     # 30 days
    QUARTER = "next_quarter"   # 90 days
    YEAR    = "next_year"      # 365 days

    # Human-readable labels used in ForecastResult.forecast_period
    @property
    def label(self) -> str:
        _labels = {
            "next_week":    "Next 7 Days",
            "next_month":   "Next 30 Days",
            "next_quarter": "Next 90 Days",
            "next_year":    "Next 365 Days",
        }
        return _labels[self.value]

    @property
    def days(self) -> int:
        _days = {
            "next_week":    7,
            "next_month":   30,
            "next_quarter": 90,
            "next_year":    365,
        }
        return _days[self.value]


# ---------------------------------------------------------------------------
# Request / Result / Context
# ---------------------------------------------------------------------------

@dataclass
class ForecastRequest:
    """
    The clean, self-contained input to ForecastEngine.

    Design decision: ForecastEngine never receives the RetrievalPlan, the
    user's question, or any LLM-related state. It only receives the minimum
    information required to produce a forecast.

    Fields:
        metric           — which business metric to forecast (strongly typed)
        forecast_horizon — the requested time window
        observations     — historical BusinessObservations to learn from
    """
    metric: ForecastMetric
    forecast_horizon: ForecastHorizon
    observations: list  # list[BusinessObservation] — typed loosely to avoid circular import


@dataclass
class ForecastResult:
    """
    A single deterministic forecast with complete provenance.

    Every field here should allow the LLM to explain the prediction
    clearly and accurately without performing any recalculation itself.

    Fields:
        metric             — the forecasted business metric (strongly typed)
        forecast_period    — human-readable period label (e.g. "Next 30 Days")
        predicted_value    — the point estimate
        confidence         — confidence in [0.0–1.0]; lower when data is sparse
        lower_bound        — lower end of the prediction interval
        upper_bound        — upper end of the prediction interval
        algorithm          — machine-readable algorithm identifier (ForecastAlgorithm enum)
        methodology        — human-readable description with parameters
                             e.g. "Exponential Smoothing (α=0.30)"
        observations_used  — number of historical data points used
        historical_period  — human label for the training window
                             e.g. "Last 90 Days (12 data points)"
    """
    metric: ForecastMetric
    forecast_period: str
    predicted_value: float
    confidence: float
    lower_bound: float
    upper_bound: float
    algorithm: ForecastAlgorithm
    methodology: str
    observations_used: int
    historical_period: str


@dataclass
class ForecastContext:
    """
    The structured output of ForecastingService.

    Consumed by RagService, which formats the results into a prompt block.
    No prompt strings are stored here — prompt assembly belongs to RagService.

    Fields:
        results      — list of individual ForecastResult objects (one per metric)
        warnings     — non-fatal issues (e.g. insufficient data for a metric)
        generated_at — UTC timestamp of when this context was produced;
                       useful for cache invalidation, logging, and audit trails
    """
    results: list[ForecastResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
