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
        
        product_quantities = {}
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            # Using canonical fields
            product = obs.key_values.get("product")
            qty_str = obs.key_values.get("quantity")
            movement = str(obs.key_values.get("movement", "")).lower()
            
            if product and qty_str:
                try:
                    qty = int(str(qty_str).replace(",", ""))
                    
                    # Assume inward movement adds to stock, outward reduces
                    if "out" in movement or "sale" in movement or "dispatch" in movement:
                        product_quantities[product] = product_quantities.get(product, 0) - qty
                    else:
                        product_quantities[product] = product_quantities.get(product, 0) + qty
                except ValueError:
                    pass

        prov_list = list(provenance)
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]

        total_stock = sum(max(0, q) for q in product_quantities.values())
        low_stock_count = sum(1 for q in product_quantities.values() if q > 0 and q < 10) # simplistic threshold

        if "stock count" in req_normalized or "total stock" in req_normalized or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Total Stock",
                metric_category=MetricCategory.RAW,
                metric_value=total_stock,
                unit="items",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "HIGH" if total_stock > 0 else "LOW",
                    "calculation_method": "Sum of net quantity per product"
                }
            ))
            
        if "low stock count" in req_normalized or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Low Stock Count",
                metric_category=MetricCategory.DERIVED,
                metric_value=low_stock_count,
                unit="items",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(product_quantities),
                    "confidence": "MEDIUM" if product_quantities else "LOW",
                    "calculation_method": "Count of products with stock < 10"
                }
            ))
            
            health = "Warning" if low_stock_count > 5 else "Healthy"
            metrics.append(BusinessMetric(
                metric_name="Inventory Health",
                metric_category=MetricCategory.HEALTH,
                metric_value=health,
                unit="",
                calculated_from=prov_list,
                metadata={
                    "calculation_method": "Warning if low_stock_count > 5"
                }
            ))

        return metrics

    def calculate_charts(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[any]:
        from schemas.dashboard import ChartSeries, ChartCategory
        charts = []
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]
        
        product_quantities = {}
        for obs in observations:
            product = obs.key_values.get("product")
            qty_str = obs.key_values.get("quantity")
            movement = str(obs.key_values.get("movement", "")).lower()
            
            if product and qty_str:
                try:
                    qty = int(str(qty_str).replace(",", ""))
                    if "out" in movement or "sale" in movement or "dispatch" in movement:
                        product_quantities[product] = product_quantities.get(product, 0) - qty
                    else:
                        product_quantities[product] = product_quantities.get(product, 0) + qty
                except ValueError:
                    pass
        
        if "inventory status" in req_normalized or "inventory_status" in required_metrics or not required_metrics:
            data = []
            if product_quantities:
                sorted_prods = sorted(product_quantities.items(), key=lambda x: x[1], reverse=True)[:10]
                for p, q in sorted_prods:
                    if q > 0:
                        data.append(ChartCategory(category=str(p), value=q))
            charts.append(ChartSeries(series_name="inventory_status", data=data))
            
        return charts


MetricRegistry.register(BusinessDomain.INVENTORY, InventoryCalculator)
