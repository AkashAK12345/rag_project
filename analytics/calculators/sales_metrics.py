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
        
        total_revenue = 0.0
        total_orders = 0
        branch_revenue = {}
        branches = set()
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            # Using canonical fields
            rev_str = obs.key_values.get("revenue")
            branch = obs.key_values.get("branch")
            
            if rev_str:
                try:
                    rev = float(str(rev_str).replace(",", "").replace("$", ""))
                    total_revenue += rev
                    total_orders += 1  # 1 row = 1 order in transactional context
                    
                    if branch:
                        branch_revenue[branch] = branch_revenue.get(branch, 0.0) + rev
                except ValueError:
                    pass

            if branch:
                branches.add(branch)

        prov_list = list(provenance)
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]

        if not required_metrics or "total revenue" in req_normalized or "total_revenue" in required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Total Revenue",
                metric_category=MetricCategory.RAW,
                metric_value=round(total_revenue, 2),
                unit="USD",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": total_orders,
                    "confidence": "HIGH" if total_revenue > 0 else "LOW",
                    "calculation_method": "Sum of revenue field"
                }
            ))
            
        if not required_metrics or "total orders" in req_normalized or "total_orders" in required_metrics or "orders" in req_normalized:
            metrics.append(BusinessMetric(
                metric_name="Total Orders",
                metric_category=MetricCategory.RAW,
                metric_value=total_orders,
                unit="count",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": total_orders,
                    "confidence": "HIGH" if total_orders > 0 else "LOW",
                    "calculation_method": "Count of valid revenue transactions"
                }
            ))
            
        if not required_metrics or "avg order value" in req_normalized or "average order value" in req_normalized or "avg_order_value" in required_metrics:
            aov = (total_revenue / total_orders) if total_orders > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Avg Order Value",
                metric_category=MetricCategory.DERIVED,
                metric_value=round(aov, 2),
                unit="USD",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": total_orders,
                    "confidence": "HIGH" if total_orders > 0 else "LOW",
                    "calculation_method": "Total Revenue / Total Orders"
                }
            ))

        if not required_metrics or "active branches" in req_normalized or "active_branches" in required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Active Branches",
                metric_category=MetricCategory.RAW,
                metric_value=len(branches),
                unit="count",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "HIGH" if branches else "LOW",
                    "calculation_method": "Count of distinct branch names"
                }
            ))

        if not required_metrics or "top branch" in req_normalized:
            if branch_revenue:
                top_branch = max(branch_revenue.items(), key=lambda x: x[1])
                metrics.append(BusinessMetric(
                    metric_name="Top Branch",
                    metric_category=MetricCategory.DERIVED,
                    metric_value=top_branch[0],
                    unit="branch_name",
                    calculated_from=prov_list,
                    metadata={
                        "branch_revenue": top_branch[1],
                        "derived_from_rows": total_orders,
                        "confidence": "HIGH",
                        "calculation_method": "Branch with highest sum of revenue"
                    }
                ))

        return metrics

    def calculate_charts(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[any]:
        from schemas.dashboard import ChartSeries, ChartCategory, ChartPoint
        charts = []
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]
        
        branch_revenue = {}
        product_qty = {}
        date_revenue = {}
        
        for obs in observations:
            branch = obs.key_values.get("branch")
            product = obs.key_values.get("product")
            qty_str = obs.key_values.get("quantity")
            rev_str = obs.key_values.get("revenue")
            t_date = obs.key_values.get("transaction_date")
            
            rev = 0.0
            if rev_str:
                try:
                    rev = float(str(rev_str).replace(",", "").replace("$", ""))
                except ValueError:
                    pass
                    
            qty = 0
            if qty_str:
                try:
                    qty = int(str(qty_str).replace(",", ""))
                except ValueError:
                    pass
            
            if branch and rev > 0:
                branch_revenue[branch] = branch_revenue.get(branch, 0.0) + rev
                
            if product and qty > 0:
                product_qty[product] = product_qty.get(product, 0) + qty
                
            if t_date and rev > 0:
                date_revenue[t_date] = date_revenue.get(t_date, 0.0) + rev
                
        if "branch performance" in req_normalized or "branch_performance" in required_metrics or not required_metrics:
            data = []
            for b, r in branch_revenue.items():
                data.append(ChartCategory(category=str(b), value=r))
            charts.append(ChartSeries(series_name="branch_performance", data=data))
            
        if "top products" in req_normalized or "top_products" in required_metrics or not required_metrics:
            data = []
            if product_qty:
                sorted_prods = sorted(product_qty.items(), key=lambda x: x[1], reverse=True)[:5]
                for p, q in sorted_prods:
                    data.append(ChartCategory(category=str(p), value=q))
            charts.append(ChartSeries(series_name="top_products", data=data))
            
        if "revenue trend" in req_normalized or "revenue_trend" in required_metrics or not required_metrics:
            data = []
            for d in sorted(date_revenue.keys()):
                data.append(ChartPoint(label=str(d), value=date_revenue[d]))
            charts.append(ChartSeries(series_name="revenue_trend", data=data))
            
        return charts


MetricRegistry.register(BusinessDomain.SALES, SalesCalculator)
