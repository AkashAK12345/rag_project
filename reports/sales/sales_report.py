import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class SalesReport(BaseReport):
    """Parses standard daily/monthly sales exports."""
    
    BUSINESS_DOMAIN = BusinessDomain.SALES
    REPORT_NAMES = ["Sales Report", "Sales Register", "Transaction Log"]
    KEYWORDS = ["sales", "sale", "revenue", "transactions"]
    
    REQUIRED_FIELDS = ["product", "revenue"]
    OPTIONAL_FIELDS = ["quantity", "transaction_date", "category", "branch"]
    
    COVERAGE = {
        "metrics": ["total_revenue", "total_orders", "avg_order_value", "active_branches"],
        "charts": ["revenue_trend", "top_products", "branch_performance"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if any(c in norm.columns for c in ["product", "revenue", "quantity"]):
                return
        raise ValueError("Sales report must contain product, quantity, or revenue columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("transaction_date")):
                    parts.append(f"Sales Date: {row['transaction_date']}")
                if pd.notna(row.get("product")):
                    parts.append(f"Product Sold: {row['product']}")
                if pd.notna(row.get("category")):
                    parts.append(f"Category: {row['category']}")
                if pd.notna(row.get("branch")):
                    parts.append(f"Branch: {row['branch']}")
                if pd.notna(row.get("quantity")):
                    parts.append(f"Quantity Sold: {row['quantity']}")
                if pd.notna(row.get("revenue")):
                    parts.append(f"Revenue: {row['revenue']}")
                known = {"transaction_date", "product", "category", "branch", "quantity", "revenue"}
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
                        report_type=ReportType.SALES,
                        business_domain=BusinessDomain.SALES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"key_values_json": json.dumps(canonical_dict)}
                    ))
        return ReportResult(
            report_type=ReportType.SALES,
            report_name="Sales Report",
            business_domain=BusinessDomain.SALES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
