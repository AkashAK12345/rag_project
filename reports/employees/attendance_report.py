import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class AttendanceReport(BaseReport):
    """Parses daily/monthly attendance logs."""
    
    BUSINESS_DOMAIN = BusinessDomain.EMPLOYEES
    REPORT_NAMES = ["Attendance Report", "Time and Attendance"]
    KEYWORDS = ["attendance", "timesheet", "clock", "presence"]
    
    REQUIRED_FIELDS = ["employee_id", "attendance_date"]
    OPTIONAL_FIELDS = ["status", "shift", "location", "hours_worked"]
    
    COVERAGE = {
        "metrics": ["attendance_rate", "headcount"],
        "charts": ["attendance_trend", "department_distribution"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            has_emp = any("employee_id" in str(c) for c in norm.columns)
            has_status = any("status" in str(c) for c in norm.columns)
            if has_emp and has_status:
                return
        raise ValueError("Attendance report must contain employee_id and status columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("attendance_date")):
                    parts.append(f"Date: {row['attendance_date']}")
                if pd.notna(row.get("employee_id")):
                    parts.append(f"Employee ID: {row['employee_id']}")
                if pd.notna(row.get("status")):
                    parts.append(f"Attendance Status: {row['status']}")
                
                known = {"attendance_date", "employee_id", "status"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    # Capture canonical fields for metadata
                    canonical_dict = {
                        str(col): str(val) for col, val in row.items() if pd.notna(val)
                    }
                    import json
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.ATTENDANCE,
                        business_domain=BusinessDomain.EMPLOYEES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"key_values_json": json.dumps(canonical_dict)}
                    ))
        return ReportResult(
            report_type=ReportType.ATTENDANCE,
            report_name="Attendance Report",
            business_domain=BusinessDomain.EMPLOYEES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
