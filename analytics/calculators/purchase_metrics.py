"""
analytics/calculators/purchase_metrics.py

Deterministic calculator for the Purchases domain.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class PurchaseCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        total_cost = 0.0
        supplier_spend = {}
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            cost_str = obs.key_values.get("cost", "0").replace(",", "").replace("$", "")
            supplier = obs.key_values.get("supplier", "Unknown")
            
            try:
                cost = float(cost_str)
                total_cost += cost
                supplier_spend[supplier] = supplier_spend.get(supplier, 0.0) + cost
            except ValueError:
                pass

        prov_list = list(provenance)

        req_lower = [m.lower() for m in required_metrics]

        if "purchase cost" in req_lower or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Purchase Cost",
                metric_category=MetricCategory.RAW,
                metric_value=round(total_cost, 2),
                unit="USD",
                calculated_from=prov_list
            ))
            
        if "top supplier" in req_lower or not required_metrics:
            if supplier_spend:
                top_supplier = max(supplier_spend.items(), key=lambda x: x[1])
                metrics.append(BusinessMetric(
                    metric_name="Top Supplier",
                    metric_category=MetricCategory.DERIVED,
                    metric_value=top_supplier[0],
                    unit="supplier_name",
                    calculated_from=prov_list,
                    metadata={"spend": top_supplier[1]}
                ))

        return metrics

MetricRegistry.register(BusinessDomain.PURCHASES, PurchaseCalculator)
