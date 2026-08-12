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
            
            # Use canonical fields only
            cost_str = obs.key_values.get("purchase_value")
            supplier = obs.key_values.get("supplier")
            
            if cost_str:
                try:
                    cost = float(str(cost_str).replace(",", "").replace("$", ""))
                    total_cost += cost
                    if supplier:
                        supplier_spend[supplier] = supplier_spend.get(supplier, 0.0) + cost
                except ValueError:
                    pass

        prov_list = list(provenance)
        req_lower = [m.lower().replace("_", " ") for m in required_metrics]

        if "purchase cost" in req_lower or "purchase value" in req_lower or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Purchase Cost",
                metric_category=MetricCategory.RAW,
                metric_value=round(total_cost, 2),
                unit="USD",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "HIGH" if total_cost > 0 else "LOW",
                    "calculation_method": "Sum of purchase_value field"
                }
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
                    metadata={
                        "spend": top_supplier[1],
                        "derived_from_rows": len(observations),
                        "confidence": "HIGH",
                        "calculation_method": "Supplier with max sum of purchase_value"
                    }
                ))

        return metrics

    def calculate_charts(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[any]:
        from schemas.dashboard import ChartSeries, ChartCategory, ChartPoint
        charts = []
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]
        
        supplier_spend = {}
        date_spend = {}
        
        for obs in observations:
            cost_str = obs.key_values.get("purchase_value")
            supplier = obs.key_values.get("supplier")
            p_date = obs.key_values.get("purchase_date")
            
            cost = 0.0
            if cost_str:
                try:
                    cost = float(str(cost_str).replace(",", "").replace("$", ""))
                except ValueError:
                    pass
            
            if cost > 0:
                if supplier:
                    supplier_spend[supplier] = supplier_spend.get(supplier, 0.0) + cost
                if p_date:
                    date_spend[p_date] = date_spend.get(p_date, 0.0) + cost

        if "supplier ranking" in req_normalized or "supplier_ranking" in required_metrics or not required_metrics:
            data = []
            if supplier_spend:
                # Top 10 suppliers by spend
                sorted_sups = sorted(supplier_spend.items(), key=lambda x: x[1], reverse=True)[:10]
                for s, v in sorted_sups:
                    data.append(ChartCategory(category=s, value=v))
            charts.append(ChartSeries(series_name="supplier_ranking", data=data))
            
        if "purchase trend" in req_normalized or "purchase_trend" in required_metrics or not required_metrics:
            data = []
            if date_spend:
                for d in sorted(date_spend.keys()):
                    data.append(ChartPoint(label=str(d), value=date_spend[d]))
            charts.append(ChartSeries(series_name="purchase_trend", data=data))
            
        return charts


MetricRegistry.register(BusinessDomain.PURCHASES, PurchaseCalculator)
