"""
schemas/retrieval_plan.py

Pure data structures describing what the intent analyzer determined
and what the retrieval layer should execute.

Design decision: plain dataclasses so this layer has zero coupling to
FastAPI, SQLAlchemy, or LlamaIndex — fully portable and unit-testable.

QueryType   → how the user wants to interact with the data
QueryIntent → the fully analyzed intent with domain classification
RetrievalPlan → the executable specification passed to RetrievalService
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

from schemas.report import BusinessDomain, ReportType
from schemas.forecast_context import ForecastMetric, ForecastHorizon


class QueryType(str, Enum):
    """
    High-level query categories that shape how context should be assembled
    and what the LLM prompt strategy should emphasize.
    """
    LOOKUP = "lookup"               # Simple factual retrieval (who, what, when, where)
    SUMMARIZE = "summarize"         # Aggregate / overview request
    COMPARE = "compare"             # Two or more entities side-by-side
    TREND = "trend"                 # Change over time
    ANOMALY = "anomaly"             # Something unusual or unexpected
    RECOMMENDATION = "recommendation"  # Action or advice request
    EXPLAIN = "explain"             # Why / how something happened
    ROOT_CAUSE = "root_cause"       # Multi-domain causal chain analysis


class QueryIntent(str, Enum):
    """
    Fine-grained intent labels. A single intent is chosen per query.
    These map loosely onto QueryType but are more specific — for example,
    IDENTIFY_TOP_PERFORMER is a more precise LOOKUP than a generic "find item".
    """
    LOOKUP_VALUE = "lookup_value"
    SUMMARIZE_REPORT = "summarize_report"
    COMPARE_ENTITIES = "compare_entities"
    IDENTIFY_TOP_PERFORMER = "identify_top_performer"
    IDENTIFY_BOTTOM_PERFORMER = "identify_bottom_performer"
    IDENTIFY_TREND = "identify_trend"
    IDENTIFY_ANOMALY = "identify_anomaly"
    REQUEST_RECOMMENDATION = "request_recommendation"
    EXPLAIN_CAUSE = "explain_cause"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"    # Multi-domain causal chain
    GENERAL = "general"


@dataclass
class TimeRange:
    """
    Optional time restriction applied by RetrievalService when filtering.

    All fields are optional — any combination creates a valid filter.
    label is a human-readable description used in logging and context headers.
    """
    label: str = ""               # e.g. "last week", "July 2025"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class RetrievalPlan:
    """
    Executable retrieval specification produced by IntentService.

    QueryService passes this directly to RetrievalService.
    It contains everything the retriever needs: which domains and report types
    to search within, how many documents to fetch, and a confidence score
    that can be logged for observability and used by future adaptive agents.

    Fields:
        query_type      — broad interaction category (LOOKUP, COMPARE, etc.)
        intent          — fine-grained intent label
        domains         — list of BusinessDomain values to restrict the search
        report_types    — list of ReportType values to further restrict (empty = all)
        top_k           — number of documents to retrieve from the vector store
        confidence      — analyzer confidence in [0.0, 1.0]; 1.0 = certain, 0.0 = fallback
        time_range      — optional time window filter; None = no time restriction
        metadata_hints  — any additional key-value pairs for future filter extensions
    """
    query_type: QueryType
    intent: QueryIntent
    domains: list[BusinessDomain]
    report_types: list[ReportType] = field(default_factory=list)
    top_k: int = 5
    confidence: float = 1.0
    time_range: Optional[TimeRange] = None
    required_metrics: list[str] = field(default_factory=list)
    metadata_hints: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Forecasting capability flags
    # These are populated by IntentService when the user's question contains
    # forecast intent. An empty list means no forecast was requested and
    # ForecastingService will be skipped entirely.
    # ------------------------------------------------------------------
    forecast_metrics: list[ForecastMetric] = field(default_factory=list)
    forecast_horizon: Optional[ForecastHorizon] = None
