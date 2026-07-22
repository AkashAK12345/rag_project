"""
analytics/calculators/employee_metrics.py

Deterministic calculator for the Employees domain.
"""

from typing import List
from analytics.base_metric import BaseCalculator
from analytics.metric_registry import MetricRegistry
from schemas.report import BusinessDomain
from schemas.query_context import BusinessObservation
from schemas.business_metric import BusinessMetric, MetricCategory


class EmployeeCalculator(BaseCalculator):
    
    def calculate(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[BusinessMetric]:
        metrics = []
        
        total_employees = 0
        total_absent = 0
        turnover_count = 0
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            employees = obs.key_values.get("employees", "0")
            absent = obs.key_values.get("absent", "0")
            turnover = obs.key_values.get("turnover", "0")
            
            try:
                total_employees += int(employees)
                total_absent += int(absent)
                turnover_count += int(turnover)
            except ValueError:
                pass

        prov_list = list(provenance)
        req_lower = [m.lower() for m in required_metrics]

        if "attendance" in req_lower or "attendance %" in req_lower or not required_metrics:
            attendance = ((total_employees - total_absent) / total_employees * 100) if total_employees > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Attendance",
                metric_category=MetricCategory.RATIO,
                metric_value=round(attendance, 2),
                unit="%",
                calculated_from=prov_list
            ))
            
        if "turnover rate" in req_lower or not required_metrics:
            turnover_rate = (turnover_count / total_employees * 100) if total_employees > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Turnover Rate",
                metric_category=MetricCategory.RATIO,
                metric_value=round(turnover_rate, 2),
                unit="%",
                calculated_from=prov_list
            ))

        return metrics

MetricRegistry.register(BusinessDomain.EMPLOYEES, EmployeeCalculator)
