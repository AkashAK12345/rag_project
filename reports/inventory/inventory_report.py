import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class InventoryReport(BaseReport):
    """Parses general inventory movement / log reports."""
    
    BUSINESS_DOMAIN = BusinessDomain.INVENTORY
    REPORT_NAMES = ["Inventory Report", "Stock Movement", "Inventory Log"]
    KEYWORDS = ["inventory", "movement", "stock", "log"]
    
    REQUIRED_FIELDS = ["product", "movement"]
    OPTIONAL_FIELDS = ["quantity", "transaction_date", "location", "batch"]
    
    COVERAGE = {
        "metrics": ["total_stock", "low_stock_count"],
        "charts": ["inventory_status", "movement_trend"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if any(c in norm.columns for c in ["product", "movement"]):
                return
        raise ValueError("Inventory report must contain product and movement columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("transaction_date")):
                    parts.append(f"Date: {row['transaction_date']}")
                if pd.notna(row.get("product")):
                    parts.append(f"Product: {row['product']}")
                if pd.notna(row.get("movement")):
                    parts.append(f"Movement Type: {row['movement']}")
                if pd.notna(row.get("quantity")):
                    parts.append(f"Quantity: {row['quantity']}")
                
                known = {"transaction_date", "product", "movement", "quantity"}
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
                        report_type=ReportType.INVENTORY,
                        business_domain=BusinessDomain.INVENTORY,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"key_values_json": json.dumps(canonical_dict)}
                    ))
        return ReportResult(
            report_type=ReportType.INVENTORY,
            report_name="Inventory Report",
            business_domain=BusinessDomain.INVENTORY,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
