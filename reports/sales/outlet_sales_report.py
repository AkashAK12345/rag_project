import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class OutletSalesReport(BaseReport):
    """Parses multi-outlet / branch-level sales performance reports."""
    
    BUSINESS_DOMAIN = BusinessDomain.SALES
    REPORT_NAMES = ["Outlet Sales", "Branch Performance", "Store Sales"]
    KEYWORDS = ["outlet", "branch", "location", "store"]
    
    REQUIRED_FIELDS = ["branch", "revenue"]
    OPTIONAL_FIELDS = ["transaction_date", "transactions"]
    
    COVERAGE = {
        "metrics": ["total_revenue", "active_branches"],
        "charts": ["branch_performance"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if "outlet" in norm.columns or "branch" in norm.columns:
                return
        raise ValueError("Outlet sales report must contain an 'outlet' or 'branch' column.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                outlet = row.get("outlet") or row.get("branch")
                if pd.notna(outlet):
                    parts.append(f"Outlet: {outlet}")
                if pd.notna(row.get("date")):
                    parts.append(f"Date: {row['date']}")
                if pd.notna(row.get("revenue")):
                    parts.append(f"Revenue: {row['revenue']}")
                if pd.notna(row.get("transactions")):
                    parts.append(f"Transactions: {row['transactions']}")
                known = {"outlet", "branch", "date", "revenue", "transactions"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.OUTLET_SALES,
                        business_domain=BusinessDomain.SALES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"outlet": str(outlet) if pd.notna(outlet) else None},
                    ))
        return ReportResult(
            report_type=ReportType.OUTLET_SALES,
            report_name="Outlet Sales Report",
            business_domain=BusinessDomain.SALES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
