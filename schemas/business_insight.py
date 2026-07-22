"""
schemas/business_insight.py

Data structures representing derived business insights.

A BusinessInsight is NOT raw data — it is an interpretation of one or more
BusinessObservations produced by InsightBuilder.

InsightType     — the category of the insight
InsightSeverity — how urgent or significant the insight is
BusinessInsight — a single structured insight with evidence
"""

from dataclasses import dataclass, field
from enum import Enum
from schemas.report import BusinessDomain


class InsightType(str, Enum):
    """Categories of business insight that can be derived from observations."""
    PERFORMANCE_CHANGE = "performance_change"    # Revenue up/down, cost up/down
    COST_PRESSURE = "cost_pressure"              # Supplier prices, food cost rising
    INVENTORY_RISK = "inventory_risk"            # Low stock, overstock, near expiry
    WASTAGE_CONCERN = "wastage_concern"          # High spoilage, unexplained loss
    STAFFING_CONCERN = "staffing_concern"        # Absenteeism, understaffing
    PRODUCTION_SHORTFALL = "production_shortfall"# Low yield, recipe issues
    CROSS_DOMAIN_CORRELATION = "cross_domain"   # Linked events across domains
    ANOMALY_DETECTED = "anomaly_detected"        # Outlier in any metric
    POSITIVE_SIGNAL = "positive_signal"          # Revenue up, cost down, etc.
    GENERAL_OBSERVATION = "general_observation"  # Fallback


class InsightSeverity(str, Enum):
    """How much attention the insight warrants."""
    CRITICAL = "critical"     # Immediate action likely required
    WARNING = "warning"       # Should be monitored or investigated
    INFO = "info"             # Informational, no immediate action
    POSITIVE = "positive"     # Good news worth highlighting


@dataclass
class BusinessInsight:
    """
    A structured, derived business observation produced by InsightBuilder.

    Fields:
        insight_type    — category of this insight
        severity        — urgency / significance level
        domain          — primary business domain
        related_domains — other domains involved (for cross-domain insights)
        headline        — one-line human-readable summary
        evidence        — the key_values or raw text that supports this insight
        source_files    — files this insight was drawn from
    """
    insight_type: InsightType
    severity: InsightSeverity
    domain: BusinessDomain
    headline: str
    related_domains: list[BusinessDomain] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
