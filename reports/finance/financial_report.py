import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class FinancialReport(BaseReport):
    """Parses general ledgers, P&L, or cash flow statements."""
    
    BUSINESS_DOMAIN = BusinessDomain.FINANCE
    REPORT_NAMES = ["Financial Report", "General Ledger", "Profit and Loss"]
    KEYWORDS = ["finance", "ledger", "pnl", "profit", "loss", "balance sheet", "accounting"]
    
    REQUIRED_FIELDS = ["amount", "account_type"]
    OPTIONAL_FIELDS = ["transaction_date", "category", "cost_center"]
    
    COVERAGE = {
        "metrics": ["profit", "gross_margin", "total_expenses"],
        "charts": ["profit_trend", "expense_distribution"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if any(c in norm.columns for c in ["account_type", "amount"]):
                return
        raise ValueError("Financial report must contain account_type and amount columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("transaction_date")):
                    parts.append(f"Date: {row['transaction_date']}")
                if pd.notna(row.get("account_type")):
                    parts.append(f"Account: {row['account_type']}")
                if pd.notna(row.get("amount")):
                    parts.append(f"Amount: {row['amount']}")
                
                known = {"transaction_date", "account_type", "amount"}
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
                        report_type=ReportType.FINANCIAL,
                        business_domain=BusinessDomain.FINANCE,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"key_values_json": json.dumps(canonical_dict)}
                    ))
        return ReportResult(
            report_type=ReportType.FINANCIAL,
            report_name="Financial Report",
            business_domain=BusinessDomain.FINANCE,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
