import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class EmployeeReport(BaseReport):
    """Parses employee master / payroll / roster reports."""
    
    BUSINESS_DOMAIN = BusinessDomain.EMPLOYEES
    REPORT_NAMES = ["Employee Master", "Payroll", "Staff Roster"]
    KEYWORDS = ["employee", "staff", "roster", "payroll"]
    
    REQUIRED_FIELDS = ["employee_id"]
    OPTIONAL_FIELDS = ["department", "designation", "status", "join date", "salary"]
    
    COVERAGE = {
        "metrics": ["headcount", "turnover_rate"],
        "charts": ["department_distribution", "designation_distribution"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            has_emp = any("employee_id" in str(c) for c in norm.columns)
            has_other = any(any(req in str(c) for c in norm.columns) for req in ["designation", "salary", "department"])
            if has_emp and has_other:
                return
        raise ValueError("Employee report must contain employee_id and designation/department/salary columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("employee_id")):
                    parts.append(f"Employee ID: {row['employee_id']}")
                if pd.notna(row.get("designation")):
                    parts.append(f"Role: {row['designation']}")
                if pd.notna(row.get("department")):
                    parts.append(f"Department: {row['department']}")
                if pd.notna(row.get("status")):
                    parts.append(f"Status: {row['status']}")
                if pd.notna(row.get("join date")):
                    parts.append(f"Join Date: {row['join date']}")
                if pd.notna(row.get("salary")):
                    parts.append(f"Salary: {row['salary']}")
                
                known = {"employee_id", "designation", "department", "status", "join date", "salary"}
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
                        report_type=ReportType.EMPLOYEE,
                        business_domain=BusinessDomain.EMPLOYEES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"key_values_json": json.dumps(canonical_dict)}
                    ))
        return ReportResult(
            report_type=ReportType.EMPLOYEE,
            report_name="Employee Report",
            business_domain=BusinessDomain.EMPLOYEES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
