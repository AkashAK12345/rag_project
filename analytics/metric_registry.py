"""
analytics/metric_registry.py

Registry pattern for mapping BusinessDomains to their Metric Calculators.
"""

from typing import Dict, Type
from analytics.base_metric import BaseCalculator
from schemas.report import BusinessDomain


class MetricRegistry:
    """
    Central registry for available business domain calculators.
    Avoids switch/if-else statements when instantiating domain calculators.
    Supports multiple calculators per domain.
    """
    
    _registry: Dict[BusinessDomain, List[Type[BaseCalculator]]] = {}

    @classmethod
    def register(cls, domain: BusinessDomain, calculator_class: Type[BaseCalculator]) -> None:
        """Register a new calculator for a business domain."""
        if domain not in cls._registry:
            cls._registry[domain] = []
        cls._registry[domain].append(calculator_class)

    @classmethod
    def get(cls, domain: BusinessDomain) -> List[Type[BaseCalculator]]:
        """Retrieve the calculator classes for the given domain."""
        return cls._registry.get(domain, [])
