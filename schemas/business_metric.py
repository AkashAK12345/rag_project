"""
schemas/business_metric.py

Structured representation of a calculated business metric.
Produced deterministically by the Business Analytics Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List


class MetricCategory(str, Enum):
    RAW = "raw"                   # e.g., Total Revenue, Total Wastage
    DERIVED = "derived_kpi"       # e.g., Average Order Value
    RATIO = "ratio"               # e.g., Food Cost Percentage
    HEALTH = "health_indicator"   # e.g., "Critical", "Healthy"


@dataclass
class BusinessMetric:
    """
    A purely deterministic, mathematically calculated metric.
    
    Fields:
        metric_name: Human-readable name (e.g. "Food Cost Percentage")
        metric_category: Enum categorizing the metric type
        metric_value: The computed numeric or categorical value
        unit: String representing the unit (e.g., "%", "USD", "orders")
        confidence: 0.0 to 1.0 (lower if data is sparse or incomplete)
        calculated_from: List of source files/datasets used in calculation (provenance)
        calculation_timestamp: When the metric was computed
        metadata: Any extra contextual info (e.g., formula used)
    """
    metric_name: str
    metric_category: MetricCategory
    metric_value: float | str
    unit: str
    
    calculated_from: List[str] = field(default_factory=list)
    confidence: float = 1.0
    calculation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
