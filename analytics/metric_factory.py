"""
analytics/metric_factory.py

Factory for instantiating Metric Calculators dynamically.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain

# ---------------------------------------------------------------------------
# Calculator modules are imported here to trigger self-registration.
# Each module calls MetricRegistry.register() at import time (module-level
# side effect), exactly mirroring the forecasting.strategy_factory pattern.
# ---------------------------------------------------------------------------
import analytics.calculators.finance_metrics    # noqa: F401
import analytics.calculators.sales_metrics      # noqa: F401
import analytics.calculators.revenue_metrics    # noqa: F401
import analytics.calculators.inventory_metrics  # noqa: F401
import analytics.calculators.employee_metrics   # noqa: F401
import analytics.calculators.purchase_metrics   # noqa: F401
import analytics.calculators.wastage_metrics    # noqa: F401


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
