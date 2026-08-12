"""
analytics/calculators/revenue_metrics.py

Deterministic calculator for Revenue-specific metrics within the Sales domain.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class RevenueCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        total_revenue = 0.0
        months = set()
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            rev_str = obs.key_values.get("revenue", "0").replace(",", "").replace("$", "")
            month = obs.key_values.get("month", None)
            
            try:
                total_revenue += float(rev_str)
                if month:
                    months.add(month)
            except ValueError:
                pass

        prov_list = list(provenance)
        # Normalize required_metrics: convert snake_case to space-separated for matching
        req_lower = [m.lower().replace("_", " ") for m in required_metrics]

        if "average monthly revenue" in req_lower or not required_metrics:
            if months:
                avg_monthly = total_revenue / len(months)
                metrics.append(BusinessMetric(
                    metric_name="Average Monthly Revenue",
                    metric_category=MetricCategory.DERIVED,
                    metric_value=round(avg_monthly, 2),
                    unit="USD",
                    calculated_from=prov_list
                ))
            
        if "revenue growth pct" in req_lower or "revenue growth" in req_lower or not required_metrics:
            # Simplistic growth placeholder
            # In reality, needs temporal ordering
            metrics.append(BusinessMetric(
                metric_name="Revenue Growth Pct",
                metric_category=MetricCategory.RATIO,
                metric_value=0.0,
                unit="%",
                calculated_from=prov_list,
                metadata={"note": "Requires temporal sorting"}
            ))

        return metrics

    def calculate_charts(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[any]:
        from schemas.dashboard import ChartSeries, RevenueTrendPoint
        charts = []
        
        # In a real scenario, this would aggregate `obs.key_values.get('date')` and `obs.key_values.get('revenue')`
        # For now, return empty data since we rely on actual observation data.
        trend_data = []
        
        if "revenue_trend" in required_metrics or not required_metrics:
            charts.append(ChartSeries(series_name="revenue_trend", data=trend_data))
            
        return charts


MetricRegistry.register(BusinessDomain.SALES, RevenueCalculator)
