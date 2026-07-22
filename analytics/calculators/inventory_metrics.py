"""
analytics/calculators/inventory_metrics.py

Deterministic calculator for the Inventory domain.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class InventoryCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        total_value = 0.0
        low_stock_count = 0
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            value_str = obs.key_values.get("value", "0").replace(",", "").replace("$", "")
            stock_str = obs.key_values.get("stock", "0").replace(",", "")
            
            try:
                total_value += float(value_str)
            except ValueError:
                pass
                
            try:
                stock = float(stock_str)
                if stock < 10.0:  # simplistic threshold for demonstration
                    low_stock_count += 1
            except ValueError:
                pass

        prov_list = list(provenance)
        req_lower = [m.lower() for m in required_metrics]

        if "stock value" in req_lower or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Stock Value",
                metric_category=MetricCategory.RAW,
                metric_value=round(total_value, 2),
                unit="USD",
                calculated_from=prov_list
            ))
            
        if "low stock count" in req_lower or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Low Stock Count",
                metric_category=MetricCategory.DERIVED,
                metric_value=low_stock_count,
                unit="items",
                calculated_from=prov_list
            ))
            
            health = "Warning" if low_stock_count > 5 else "Healthy"
            metrics.append(BusinessMetric(
                metric_name="Inventory Health",
                metric_category=MetricCategory.HEALTH,
                metric_value=health,
                unit="",
                calculated_from=prov_list
            ))

        return metrics

MetricRegistry.register(BusinessDomain.INVENTORY, InventoryCalculator)
