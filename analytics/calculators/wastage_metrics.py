"""
analytics/calculators/wastage_metrics.py

Deterministic calculator for the Wastage domain.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class WastageCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        total_waste_value = 0.0
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            value_str = obs.key_values.get("waste_value", "0").replace(",", "").replace("$", "")
            try:
                total_waste_value += float(value_str)
            except ValueError:
                pass

        prov_list = list(provenance)
        req_lower = [m.lower() for m in required_metrics]

        if "total wastage" in req_lower or "waste cost" in req_lower or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Total Wastage",
                metric_category=MetricCategory.RAW,
                metric_value=round(total_waste_value, 2),
                unit="USD",
                calculated_from=prov_list
            ))

        return metrics

MetricRegistry.register(BusinessDomain.WASTAGE, WastageCalculator)
