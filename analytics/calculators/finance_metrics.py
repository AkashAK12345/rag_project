"""
analytics/calculators/finance_metrics.py

Deterministic calculator for the Finance domain.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class FinanceCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        revenue = 0.0
        cogs = 0.0
        operating_cost = 0.0
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            rev_str = obs.key_values.get("revenue", "0").replace(",", "").replace("$", "")
            cogs_str = obs.key_values.get("cogs", "0").replace(",", "").replace("$", "")
            op_cost_str = obs.key_values.get("operating_cost", "0").replace(",", "").replace("$", "")
            
            try:
                revenue += float(rev_str)
                cogs += float(cogs_str)
                operating_cost += float(op_cost_str)
            except ValueError:
                pass

        prov_list = list(provenance)
        req_lower = [m.lower() for m in required_metrics]

        # Profit
        profit = revenue - cogs - operating_cost
        if "profit" in req_lower or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Profit",
                metric_category=MetricCategory.RAW,
                metric_value=round(profit, 2),
                unit="USD",
                calculated_from=prov_list
            ))
            
        # Gross Margin %
        if "gross margin" in req_lower or not required_metrics:
            margin = ((revenue - cogs) / revenue * 100) if revenue > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Gross Margin",
                metric_category=MetricCategory.RATIO,
                metric_value=round(margin, 2),
                unit="%",
                calculated_from=prov_list
            ))
            
        # Food Cost % (assuming COGS represents food cost in this context)
        if "food cost" in req_lower or "food cost %" in req_lower or not required_metrics:
            food_cost_pct = (cogs / revenue * 100) if revenue > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Food Cost",
                metric_category=MetricCategory.RATIO,
                metric_value=round(food_cost_pct, 2),
                unit="%",
                calculated_from=prov_list
            ))
            
            health = "Warning" if food_cost_pct > 35 else "Healthy"
            metrics.append(BusinessMetric(
                metric_name="Food Cost Health",
                metric_category=MetricCategory.HEALTH,
                metric_value=health,
                unit="",
                calculated_from=prov_list
            ))

        return metrics

MetricRegistry.register(BusinessDomain.FINANCE, FinanceCalculator)
