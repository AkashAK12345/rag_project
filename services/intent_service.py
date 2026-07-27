"""
services/intent_service.py

Intent analysis layer for the Business Query Intelligence pipeline.

Architecture decision:
    BaseIntentAnalyzer defines the interface contract.
    RuleBasedIntentAnalyzer provides the deterministic, zero-latency implementation.
    A future LLMIntentAnalyzer (or LangGraph-driven planner) can be dropped in
    by registering a new subclass — QueryService never changes.

The rule-based engine works by scanning the normalized query against
domain-specific keyword signatures and intent pattern vocabularies.
Each match contributes to a confidence score, and the highest-scoring
domain set and intent combination wins.

Confidence scoring:
    - 1.0  → strong, unambiguous multi-keyword match
    - 0.7  → moderate single-keyword match with domain signal
    - 0.4  → weak / inferred from context
    - 0.1  → complete fallback (no pattern matched)
"""

from abc import ABC, abstractmethod
from datetime import date, timedelta

from core.logging import get_logger
from schemas.report import BusinessDomain, ReportType
from schemas.retrieval_plan import QueryIntent, QueryType, RetrievalPlan, TimeRange
from schemas.forecast_context import ForecastHorizon, ForecastMetric

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Interface contract
# ---------------------------------------------------------------------------

class BaseIntentAnalyzer(ABC):
    """
    Abstract interface for intent analyzers.
    QueryService depends only on this interface, not on any implementation.
    """

    @abstractmethod
    def analyze(self, question: str) -> RetrievalPlan:
        """
        Analyze the natural language question and produce a RetrievalPlan.

        Args:
            question: The user's raw natural language question.

        Returns:
            A fully populated RetrievalPlan ready for RetrievalService.
        """
        ...


# ---------------------------------------------------------------------------
# Domain keyword signatures
# Each tuple: (set of keywords, matched BusinessDomain, relevant ReportTypes)
# ---------------------------------------------------------------------------

_DOMAIN_RULES: list[tuple[set[str], BusinessDomain, list[ReportType]]] = [
    (
        {"sales", "revenue", "sold", "transaction", "outlet", "branch",
         "top selling", "best selling", "worst selling", "low sales"},
        BusinessDomain.SALES,
        [ReportType.SALES, ReportType.OUTLET_SALES],
    ),
    (
        {"purchase", "procurement", "supplier", "vendor", "order", "po",
         "bought", "acquired", "purchasing"},
        BusinessDomain.PURCHASES,
        [ReportType.PURCHASES],
    ),
    (
        {"inventory", "stock", "expiry", "expiration", "on hand",
         "storage", "warehouse", "spoilage", "shelf"},
        BusinessDomain.INVENTORY,
        [ReportType.INVENTORY, ReportType.STOCK, ReportType.EXPIRY],
    ),
    (
        {"food cost", "cost of goods", "cogs", "profit", "loss", "margin",
         "finance", "financial", "ledger", "balance", "expense", "budget"},
        BusinessDomain.FINANCE,
        [ReportType.FINANCIAL],
    ),
    (
        {"employee", "staff", "attendance", "payroll", "hours", "absent",
         "present", "leave", "hr", "roster"},
        BusinessDomain.EMPLOYEES,
        [ReportType.EMPLOYEE, ReportType.ATTENDANCE],
    ),
    (
        {"production", "recipe", "yield", "batch", "cook", "prepared",
         "manufactured", "kitchen", "output"},
        BusinessDomain.PRODUCTION,
        [ReportType.PRODUCTION],
    ),
    (
        {"wastage", "waste", "spoiled", "damaged", "discarded", "loss",
         "thrown", "disposal", "shrinkage"},
        BusinessDomain.WASTAGE,
        [ReportType.WASTAGE],
    ),
]

# ---------------------------------------------------------------------------
# Intent pattern vocabulary
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: list[tuple[set[str], QueryIntent, QueryType, int]] = [
    # (keywords, intent, query_type, score_weight)
    (
        {"highest", "top", "most", "best", "maximum", "leading", "rank"},
        QueryIntent.IDENTIFY_TOP_PERFORMER, QueryType.LOOKUP, 3,
    ),
    (
        {"lowest", "bottom", "least", "worst", "minimum", "poor"},
        QueryIntent.IDENTIFY_BOTTOM_PERFORMER, QueryType.LOOKUP, 3,
    ),
    (
        {"compare", "vs", "versus", "difference", "differ", "against",
         "contrast", "relative"},
        QueryIntent.COMPARE_ENTITIES, QueryType.COMPARE, 4,
    ),
    (
        {"trend", "over time", "growing", "declining", "increase",
         "decrease", "month", "week", "quarter", "year", "period"},
        QueryIntent.IDENTIFY_TREND, QueryType.TREND, 3,
    ),
    (
        {"anomaly", "unusual", "unexpected", "spike", "drop", "sudden",
         "outlier", "weird", "strange"},
        QueryIntent.IDENTIFY_ANOMALY, QueryType.ANOMALY, 4,
    ),
    (
        {"why", "cause", "reason", "because", "due to", "explain",
         "what led", "how did"},
        QueryIntent.EXPLAIN_CAUSE, QueryType.EXPLAIN, 3,
    ),
    (
        {"recommend", "suggestion", "advice", "should", "what to do",
         "improve", "action", "next step"},
        QueryIntent.REQUEST_RECOMMENDATION, QueryType.RECOMMENDATION, 4,
    ),
    (
        {"root cause", "what caused", "main reason", "primary reason",
         "chain of events", "domino", "downstream", "impact of",
         "correlation", "relationship between", "connected to"},
        QueryIntent.ROOT_CAUSE_ANALYSIS, QueryType.ROOT_CAUSE, 5,
    ),
    (
        {"summarize", "summary", "overview", "report", "total",
         "overall", "aggregate", "how much"},
        QueryIntent.SUMMARIZE_REPORT, QueryType.SUMMARIZE, 2,
    ),
    (
        {"what is", "show", "find", "list", "get", "fetch", "display",
         "which", "who"},
        QueryIntent.LOOKUP_VALUE, QueryType.LOOKUP, 1,
    ),
]


# ---------------------------------------------------------------------------
# Forecast keyword vocabulary
# ---------------------------------------------------------------------------

# Keywords that signal a forecast is being requested
_FORECAST_TRIGGER_KEYWORDS: set[str] = {
    "forecast", "predict", "projection", "projected", "expected",
    "anticipated", "estimate", "future", "outlook", "next",
}

# Metric keywords → ForecastMetric enum value
_FORECAST_METRIC_RULES: list[tuple[set[str], ForecastMetric]] = [
    ({"sales"}, ForecastMetric.SALES),
    ({"revenue", "income"}, ForecastMetric.REVENUE),
    ({"inventory", "stock"}, ForecastMetric.INVENTORY),
    ({"demand", "units sold", "quantity"}, ForecastMetric.DEMAND),
    ({"expense", "expenses", "cost", "expenditure"}, ForecastMetric.EXPENSES),
    ({"profit", "margin", "net profit"}, ForecastMetric.PROFIT),
    ({"branch", "outlet", "branch performance"}, ForecastMetric.BRANCH_PERFORMANCE),
    ({"purchase", "procurement", "purchasing"}, ForecastMetric.PURCHASE),
]

# Horizon keywords → ForecastHorizon enum value
_FORECAST_HORIZON_RULES: list[tuple[str, ForecastHorizon]] = [
    ("next year", ForecastHorizon.YEAR),
    ("next quarter", ForecastHorizon.QUARTER),
    ("next month", ForecastHorizon.MONTH),
    ("next week", ForecastHorizon.WEEK),
    ("this year", ForecastHorizon.YEAR),
    ("this quarter", ForecastHorizon.QUARTER),
    ("this month", ForecastHorizon.MONTH),
    ("this week", ForecastHorizon.WEEK),
]


# ---------------------------------------------------------------------------
# Rule-based implementation
# ---------------------------------------------------------------------------

class RuleBasedIntentAnalyzer(BaseIntentAnalyzer):
    """
    Deterministic, zero-latency intent analyzer using keyword pattern matching.

    Design constraints:
    - No external calls. No LLM. No I/O.
    - All scoring is additive over matched keyword sets.
    - Ties in domain scoring are broken by keyword count.
    - Falls back gracefully to UNKNOWN domain / GENERAL intent.

    Swap this class for LLMIntentAnalyzer in the future by injecting a
    different implementation into QueryService — the interface stays unchanged.
    """

    def analyze(self, question: str) -> RetrievalPlan:
        normalized = question.lower().strip()
        logger.info(f"RuleBasedIntentAnalyzer: analyzing question '{question}'")

        # 1. Classify domains
        matched_domains, matched_report_types, domain_confidence = (
            self._classify_domains(normalized)
        )

        # 2. Classify intent
        intent, query_type, intent_confidence = self._classify_intent(normalized)

        # 3. Detect time range
        time_range = self._detect_time_range(normalized)

        # 4. Combine confidence: domain drives it, intent adds a bonus
        combined_confidence = min(
            1.0,
            domain_confidence * 0.7 + intent_confidence * 0.3,
        )

        # 5. Determine top_k based on intent
        top_k = self._pick_top_k(intent)

        # 5b. Detect forecast intent (does not affect QueryType/QueryIntent)
        forecast_metrics, forecast_horizon = self._detect_forecast_request(normalized)

        plan = RetrievalPlan(
            query_type=query_type,
            intent=intent,
            domains=matched_domains,
            report_types=matched_report_types,
            top_k=top_k,
            confidence=round(combined_confidence, 3),
            time_range=time_range,
            required_metrics=self._detect_required_metrics(normalized),
            forecast_metrics=forecast_metrics,
            forecast_horizon=forecast_horizon,
        )

        forecast_log = (
            f", forecast_metrics={[m.value for m in forecast_metrics]}"
            f", forecast_horizon={forecast_horizon.value if forecast_horizon else 'default'}"
            if forecast_metrics else ""
        )
        logger.info(
            f"RetrievalPlan: intent={intent.value}, type={query_type.value}, "
            f"domains={[d.value for d in matched_domains]}, "
            f"top_k={top_k}, confidence={plan.confidence:.3f}"
            + (f", time_range={time_range.label}" if time_range else "")
            + forecast_log
        )
        return plan

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _classify_domains(
        self,
        text: str,
    ) -> tuple[list[BusinessDomain], list[ReportType], float]:
        """Score each domain rule against the query text."""
        domain_scores: dict[BusinessDomain, int] = {}
        domain_report_types: dict[BusinessDomain, list[ReportType]] = {}

        import re
        for keywords, domain, report_types in _DOMAIN_RULES:
            hit_count = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text))
            if hit_count > 0:
                domain_scores[domain] = hit_count
                domain_report_types[domain] = report_types

        if not domain_scores:
            logger.debug("No domain matched — falling back to UNKNOWN")
            return [BusinessDomain.UNKNOWN], [], 0.1

        # Sort by score descending; include all domains scoring > 0
        sorted_domains = sorted(
            domain_scores.items(), key=lambda x: x[1], reverse=True
        )

        # Collect matched domains and their report types
        top_score = sorted_domains[0][1]
        selected: list[BusinessDomain] = []
        selected_types: list[ReportType] = []

        for domain, score in sorted_domains:
            selected.append(domain)
            for rt in domain_report_types[domain]:
                if rt not in selected_types:
                    selected_types.append(rt)

        # Confidence: 1.0 if top domain has ≥3 keyword hits; 0.7 for 2; 0.4 for 1
        if top_score >= 3:
            confidence = 1.0
        elif top_score == 2:
            confidence = 0.7
        else:
            confidence = 0.4

        return selected, selected_types, confidence

    def _classify_intent(
        self,
        text: str,
    ) -> tuple[QueryIntent, QueryType, float]:
        """Score each intent pattern against the query text."""
        best_intent = QueryIntent.GENERAL
        best_type = QueryType.LOOKUP
        best_score = 0

        import re
        for keywords, intent, query_type, weight in _INTENT_PATTERNS:
            hit_count = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text))
            score = hit_count * weight
            if score > best_score:
                best_score = score
                best_intent = intent
                best_type = query_type

        # Confidence from intent signal strength
        if best_score >= 8:
            confidence = 1.0
        elif best_score >= 4:
            confidence = 0.7
        elif best_score > 0:
            confidence = 0.4
        else:
            confidence = 0.1

        return best_intent, best_type, confidence

    @staticmethod
    def _pick_top_k(intent: QueryIntent) -> int:
        """
        Determine how many documents to retrieve based on intent.
        Compare / trend / root_cause queries need more breadth; lookups need fewer.
        """
        TOP_K_MAP = {
            QueryIntent.ROOT_CAUSE_ANALYSIS: 15,
            QueryIntent.COMPARE_ENTITIES: 10,
            QueryIntent.IDENTIFY_TREND: 10,
            QueryIntent.SUMMARIZE_REPORT: 8,
            QueryIntent.EXPLAIN_CAUSE: 8,
            QueryIntent.REQUEST_RECOMMENDATION: 8,
            QueryIntent.IDENTIFY_ANOMALY: 6,
            QueryIntent.IDENTIFY_TOP_PERFORMER: 5,
            QueryIntent.IDENTIFY_BOTTOM_PERFORMER: 5,
            QueryIntent.LOOKUP_VALUE: 4,
            QueryIntent.GENERAL: 5,
        }
        return TOP_K_MAP.get(intent, 5)

    @staticmethod
    def _detect_time_range(text: str) -> "TimeRange | None":
        """
        Detect temporal intent from the query and map it to a TimeRange.
        Returns None if no time signal is found (no filter applied).
        """
        today = date.today()

        if "today" in text:
            return TimeRange(label="Today", start_date=today, end_date=today)
        if "yesterday" in text:
            yesterday = today - timedelta(days=1)
            return TimeRange(label="Yesterday", start_date=yesterday, end_date=yesterday)
        if "last week" in text or "past week" in text:
            start = today - timedelta(days=7)
            return TimeRange(label="Last Week", start_date=start, end_date=today)
        if "last month" in text or "past month" in text:
            start = today - timedelta(days=30)
            return TimeRange(label="Last Month", start_date=start, end_date=today)
        if "last quarter" in text or "past quarter" in text:
            start = today - timedelta(days=90)
            return TimeRange(label="Last Quarter", start_date=start, end_date=today)
        if "this week" in text:
            start = today - timedelta(days=today.weekday())
            return TimeRange(label="This Week", start_date=start, end_date=today)
        if "this month" in text:
            start = today.replace(day=1)
            return TimeRange(label="This Month", start_date=start, end_date=today)
        if "this year" in text or "ytd" in text:
            start = today.replace(month=1, day=1)
            return TimeRange(label="Year to Date", start_date=start, end_date=today)

        return None

    @staticmethod
    def _detect_required_metrics(text: str) -> list[str]:
        """
        Detect specific metrics requested by the user.
        In a real system, this would be an LLM or an NLP tagger.
        For now, we map keywords to metric names that our calculators support.
        """
        requested = set()
        
        # Sales
        if "revenue" in text or "sales" in text:
            requested.add("Total Revenue")
        if "order" in text:
            requested.add("Total Orders")
        if "average" in text and "order" in text:
            requested.add("Average Order Value")
        if "branch" in text:
            requested.add("Top Branch")
            
        # Finance
        if "profit" in text:
            requested.add("Profit")
        if "margin" in text:
            requested.add("Gross Margin")
        if "food cost" in text:
            requested.add("Food Cost")
            
        # Inventory
        if "stock value" in text:
            requested.add("Stock Value")
        if "low stock" in text:
            requested.add("Low Stock Count")
            
        # Purchases
        if "purchase cost" in text:
            requested.add("Purchase Cost")
        if "top supplier" in text:
            requested.add("Top Supplier")
            
        # Wastage
        if "wast" in text: # total wastage, waste cost
            requested.add("Total Wastage")
            
        # Employees
        if "attendance" in text:
            requested.add("Attendance")
        if "turnover" in text:
            requested.add("Turnover Rate")

        return list(requested)

    @staticmethod
    def _detect_forecast_request(
        text: str,
    ) -> tuple[list[ForecastMetric], ForecastHorizon | None]:
        """
        Detect whether the user is requesting a forecast and, if so,
        which metrics and horizon they want.

        Returns:
            (forecast_metrics, forecast_horizon)
            forecast_metrics: empty list if no forecast intent detected.
            forecast_horizon: None if not specified (ForecastingService applies default).
        """
        # Check for forecast trigger keywords
        has_forecast_intent = any(kw in text for kw in _FORECAST_TRIGGER_KEYWORDS)
        if not has_forecast_intent:
            return [], None

        # Identify which metrics are being requested
        matched_metrics: list[ForecastMetric] = []
        for keywords, metric in _FORECAST_METRIC_RULES:
            if any(kw in text for kw in keywords):
                if metric not in matched_metrics:
                    matched_metrics.append(metric)

        # Identify the requested horizon (most specific match wins)
        detected_horizon: ForecastHorizon | None = None
        for phrase, horizon in _FORECAST_HORIZON_RULES:
            if phrase in text:
                detected_horizon = horizon
                break  # list is ordered longest-match first

        return matched_metrics, detected_horizon
