"""
analytics/calculators/sales_metrics.py

Deterministic calculator for the Sales domain.
Computes Total Revenue, Orders, Average Order Value, Top Branch, etc.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class SalesCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        # In a real enterprise system, we would parse float(obs.key_values.get("revenue"))
        # Here we do a safe extraction with assumed standard keys
        
        total_revenue = 0.0
        total_orders = 0
        branch_revenue = {}
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            # Standard keys expected during ingestion
            rev_str = obs.key_values.get("revenue", "0").replace(",", "").replace("$", "")
            ord_str = obs.key_values.get("orders", "0").replace(",", "")
            branch = obs.key_values.get("branch", "Unknown")
            
            try:
                rev = float(rev_str)
                total_revenue += rev
                branch_revenue[branch] = branch_revenue.get(branch, 0.0) + rev
            except ValueError:
                pass
                
            try:
                orders = int(ord_str)
                total_orders += orders
            except ValueError:
                pass

        prov_list = list(provenance)

        # 1. Total Revenue
        if "total revenue" in [m.lower() for m in required_metrics] or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Total Revenue",
                metric_category=MetricCategory.RAW,
                metric_value=round(total_revenue, 2),
                unit="USD",
                calculated_from=prov_list
            ))
            
        # 2. Total Orders
        if "orders" in [m.lower() for m in required_metrics] or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Total Orders",
                metric_category=MetricCategory.RAW,
                metric_value=total_orders,
                unit="count",
                calculated_from=prov_list
            ))
            
        # 3. Average Order Value
        if "average order value" in [m.lower() for m in required_metrics] or not required_metrics:
            aov = (total_revenue / total_orders) if total_orders > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Average Order Value",
                metric_category=MetricCategory.DERIVED,
                metric_value=round(aov, 2),
                unit="USD",
                calculated_from=prov_list
            ))

        # 4. Top Branch
        if "top branch" in [m.lower() for m in required_metrics] or not required_metrics:
            if branch_revenue:
                top_branch = max(branch_revenue.items(), key=lambda x: x[1])
                metrics.append(BusinessMetric(
                    metric_name="Top Branch",
                    metric_category=MetricCategory.DERIVED,
                    metric_value=top_branch[0],
                    unit="branch_name",
                    calculated_from=prov_list,
                    metadata={"branch_revenue": top_branch[1]}
                ))

        return metrics

# Register the calculator for the SALES domain
MetricRegistry.register(BusinessDomain.SALES, SalesCalculator)
