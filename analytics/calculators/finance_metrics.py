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
        expenses = 0.0
        cogs = 0.0
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            # Use canonical fields only
            amt_str = obs.key_values.get("amount")
            acc_type = str(obs.key_values.get("account_type", "")).lower()
            
            if amt_str:
                try:
                    amt = float(str(amt_str).replace(",", "").replace("$", ""))
                    
                    # Very simple account type classification
                    if "revenue" in acc_type or "sales" in acc_type or "income" in acc_type:
                        revenue += amt
                    elif "cogs" in acc_type or "cost of goods" in acc_type or "food cost" in acc_type:
                        cogs += amt
                        expenses += amt
                    elif "expense" in acc_type or "cost" in acc_type or "operating" in acc_type:
                        expenses += amt
                    else:
                        pass
                except ValueError:
                    pass

        prov_list = list(provenance)
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]

        # Profit
        profit = revenue - expenses
        if "profit" in req_normalized or "net profit" in req_normalized or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Profit",
                metric_category=MetricCategory.RAW,
                metric_value=round(profit, 2),
                unit="USD",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "MEDIUM" if len(observations) > 0 else "LOW",
                    "calculation_method": "Sum of Revenue - Sum of Expenses"
                }
            ))
            
        # Gross Margin %
        if "gross margin" in req_normalized or "gross_margin" in required_metrics or not required_metrics:
            margin = ((revenue - cogs) / revenue * 100) if revenue > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Gross Margin",
                metric_category=MetricCategory.RATIO,
                metric_value=round(margin, 2),
                unit="%",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "MEDIUM" if revenue > 0 else "LOW",
                    "calculation_method": "(Revenue - COGS) / Revenue"
                }
            ))
            
        # Total Expenses
        if "total expenses" in req_normalized or "total_expenses" in required_metrics or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Total Expenses",
                metric_category=MetricCategory.RAW,
                metric_value=round(expenses, 2),
                unit="USD",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "MEDIUM" if len(observations) > 0 else "LOW",
                    "calculation_method": "Sum of Expense accounts"
                }
            ))

        return metrics

    def calculate_charts(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[any]:
        from schemas.dashboard import ChartSeries, ChartCategory, ChartPoint
        charts = []
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]
        
        expense_distribution = {}
        date_profit = {}
        
        for obs in observations:
            amt_str = obs.key_values.get("amount")
            acc_type = str(obs.key_values.get("account_type", "")).lower()
            t_date = obs.key_values.get("transaction_date")
            
            amt = 0.0
            if amt_str:
                try:
                    amt = float(str(amt_str).replace(",", "").replace("$", ""))
                except ValueError:
                    pass
            
            if amt > 0:
                is_expense = "expense" in acc_type or "cost" in acc_type or "cogs" in acc_type
                is_revenue = "revenue" in acc_type or "sales" in acc_type or "income" in acc_type
                
                if is_expense:
                    display_name = str(obs.key_values.get("account_type", "Unknown Expense")).title()
                    expense_distribution[display_name] = expense_distribution.get(display_name, 0.0) + amt
                    
                if t_date:
                    date_profit[t_date] = date_profit.get(t_date, 0.0)
                    if is_revenue:
                        date_profit[t_date] += amt
                    elif is_expense:
                        date_profit[t_date] -= amt

        if "expense distribution" in req_normalized or "expense_distribution" in required_metrics or not required_metrics:
            data = []
            if expense_distribution:
                for c, v in expense_distribution.items():
                    data.append(ChartCategory(category=c, value=v))
            charts.append(ChartSeries(series_name="expense_distribution", data=data))
            
        if "profit trend" in req_normalized or "profit_trend" in required_metrics or not required_metrics:
            data = []
            if date_profit:
                for d in sorted(date_profit.keys()):
                    data.append(ChartPoint(label=str(d), value=date_profit[d]))
            charts.append(ChartSeries(series_name="profit_trend", data=data))
            
        return charts


MetricRegistry.register(BusinessDomain.FINANCE, FinanceCalculator)
