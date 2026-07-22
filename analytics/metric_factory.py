"""
analytics/metric_factory.py

Factory for instantiating Metric Calculators dynamically.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain


class MetricFactory:
    """
    Creates calculator instances using the Registry.
    """
    
    @staticmethod
    def create(domain: BusinessDomain) -> List[BaseCalculator]:
        """
        Instantiate the appropriate calculators for the domain.
        
        Args:
            domain: The BusinessDomain enum value.
            
        Returns:
            A list of instantiated BaseCalculators.
        """
        calculator_classes = MetricRegistry.get(domain)
        return [calc_cls() for calc_cls in calculator_classes]
