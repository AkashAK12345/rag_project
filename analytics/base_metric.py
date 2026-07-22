"""
analytics/base_metric.py

Abstract interface for domain-specific metric calculators.
"""

from abc import ABC, abstractmethod
from typing import List

from schemas.business_metric import BusinessMetric
from schemas.query_context import BusinessObservation


class BaseCalculator(ABC):
    """
    Contract for all metric calculators.
    
    A Calculator takes a list of structured BusinessObservations (usually from a single domain)
    and computes deterministic KPIs based on the required_metrics list.
    """

    @abstractmethod
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        """
        Compute analytics from raw observations.
        
        Args:
            observations: List of factual data points extracted during ingestion.
            required_metrics: List of metric names the planner has requested.
                              If empty, calculators might compute all or none,
                              depending on the domain's default behavior.
                              
        Returns:
            A list of computed BusinessMetric objects.
        """
        ...
