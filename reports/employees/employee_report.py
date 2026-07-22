import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["employee", "role", "department", "salary", "status", "join date"]
_SHEET_KEYWORDS = ["employee", "staff", "roster", "payroll"]


class EmployeeReport(BaseReport):
    """Parses employee master / payroll / roster reports."""

    @classmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        sheet_bonus = 0.35 if cls._sheet_contains_keywords(df_map, _SHEET_KEYWORDS) else 0.0
        best_col_score = 0.0
        for df in df_map.values():
            norm = cls._normalise_columns(df)
            score = cls._columns_present(norm, _REQUIRED_COLS)
            if score > best_col_score:
                best_col_score = score
        return min(1.0, best_col_score * 0.7 + sheet_bonus)

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if "employee" in norm.columns and any(c in norm.columns for c in ["role", "salary", "department"]):
                return
        raise ValueError("Employee report must contain employee and role/department/salary columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("employee")):
                    parts.append(f"Employee: {row['employee']}")
                if pd.notna(row.get("role")):
                    parts.append(f"Role: {row['role']}")
                if pd.notna(row.get("department")):
                    parts.append(f"Department: {row['department']}")
                if pd.notna(row.get("status")):
                    parts.append(f"Status: {row['status']}")
                if pd.notna(row.get("join date")):
                    parts.append(f"Join Date: {row['join date']}")
                if pd.notna(row.get("salary")):
                    parts.append(f"Salary: {row['salary']}")
                
                known = {"employee", "role", "department", "status", "join date", "salary"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.EMPLOYEE,
                        business_domain=BusinessDomain.EMPLOYEES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.EMPLOYEE,
            report_name="Employee Report",
            business_domain=BusinessDomain.EMPLOYEES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
