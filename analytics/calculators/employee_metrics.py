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
        
        emp_ids = set()
        inactive_emps = set()
        
        attendance_days = 0
        present_days = 0
        
        provenance = set()
        
        for obs in observations:
            provenance.add(obs.source_file)
            
            # Using canonical fields
            emp_id = obs.key_values.get("employee_id")
            if emp_id:
                emp_ids.add(emp_id)
                
            status = str(obs.key_values.get("status", "")).lower()
            if status in ["inactive", "terminated", "resigned", "left"]:
                if emp_id:
                    inactive_emps.add(emp_id)
                    
            att_date = obs.key_values.get("attendance_date")
            if att_date and emp_id:
                attendance_days += 1
                if status in ["present", "p", "on time", "late"]:
                    present_days += 1

        prov_list = list(provenance)
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]

        if "headcount" in req_normalized or "total headcount" in req_normalized or not required_metrics:
            metrics.append(BusinessMetric(
                metric_name="Headcount",
                metric_category=MetricCategory.RAW,
                metric_value=len(emp_ids),
                unit="employees",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "HIGH" if emp_ids else "LOW",
                    "calculation_method": "Count of distinct employee_id"
                }
            ))

        if "attendance" in req_normalized or "attendance %" in req_normalized or "attendance rate" in req_normalized or not required_metrics:
            attendance = (present_days / attendance_days * 100) if attendance_days > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Attendance",
                metric_category=MetricCategory.RATIO,
                metric_value=round(attendance, 2),
                unit="%",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": attendance_days,
                    "confidence": "HIGH" if attendance_days > 0 else "LOW",
                    "calculation_method": "present_days / total_attendance_records"
                }
            ))
            
        if "turnover rate" in req_normalized or not required_metrics:
            turnover_rate = (len(inactive_emps) / len(emp_ids) * 100) if len(emp_ids) > 0 else 0.0
            metrics.append(BusinessMetric(
                metric_name="Turnover Rate",
                metric_category=MetricCategory.RATIO,
                metric_value=round(turnover_rate, 2),
                unit="%",
                calculated_from=prov_list,
                metadata={
                    "derived_from_rows": len(observations),
                    "confidence": "MEDIUM" if emp_ids else "LOW",
                    "calculation_method": "Inactive employees / Total distinct employees"
                }
            ))

        return metrics

    def calculate_charts(self, observations: List[BusinessObservation], required_metrics: List[str]) -> List[any]:
        from schemas.dashboard import ChartSeries, ChartCategory, ChartPoint
        charts = []
        req_normalized = [m.lower().replace("_", " ") for m in required_metrics]
        
        dept_counts = {}
        role_counts = {}
        att_trend = {}
        
        for obs in observations:
            dept = obs.key_values.get("department")
            if dept:
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
                
            role = obs.key_values.get("designation")
            if role:
                role_counts[role] = role_counts.get(role, 0) + 1
                
            att_date = obs.key_values.get("attendance_date")
            status = str(obs.key_values.get("status", "")).lower()
            if att_date:
                if att_date not in att_trend:
                    att_trend[att_date] = {"present": 0, "total": 0}
                att_trend[att_date]["total"] += 1
                if status in ["present", "p", "on time", "late"]:
                    att_trend[att_date]["present"] += 1

        if "department distribution" in req_normalized or "department_distribution" in required_metrics or not required_metrics:
            data = [ChartCategory(category=str(k), value=v) for k, v in dept_counts.items()]
            charts.append(ChartSeries(series_name="department_distribution", data=data))
            
        if "designation distribution" in req_normalized or "designation_distribution" in required_metrics or not required_metrics:
            data = [ChartCategory(category=str(k), value=v) for k, v in role_counts.items()]
            charts.append(ChartSeries(series_name="designation_distribution", data=data))
            
        if "attendance trend" in req_normalized or "attendance_trend" in required_metrics or not required_metrics:
            data = []
            for d in sorted(att_trend.keys()):
                pct = (att_trend[d]["present"] / att_trend[d]["total"] * 100) if att_trend[d]["total"] > 0 else 0
                data.append(ChartPoint(label=str(d), value=round(pct, 2)))
            charts.append(ChartSeries(series_name="attendance_trend", data=data))

        return charts


MetricRegistry.register(BusinessDomain.EMPLOYEES, EmployeeCalculator)
