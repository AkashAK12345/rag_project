import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class PurchaseReport(BaseReport):
    """Parses purchase orders and incoming procurement."""
    
    BUSINESS_DOMAIN = BusinessDomain.PURCHASES
    REPORT_NAMES = ["Purchase Report", "Procurement Log", "Vendor Orders"]
    KEYWORDS = ["purchase", "purchases", "procurement", "vendor", "po"]
    
    REQUIRED_FIELDS = ["supplier", "purchase_value"]
    OPTIONAL_FIELDS = ["product", "quantity", "unit_price", "purchase_date"]
    
    COVERAGE = {
        "metrics": ["purchase_cost", "total_orders", "top_supplier"],
        "charts": ["purchase_trend", "supplier_ranking"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if any(c in norm.columns for c in ["product", "supplier", "purchase_value"]):
                return
        raise ValueError("Purchase report must contain product, supplier, and purchase_value columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("purchase_date")):
                    parts.append(f"Purchase Date: {row['purchase_date']}")
                if pd.notna(row.get("supplier")):
                    parts.append(f"Supplier: {row['supplier']}")
                if pd.notna(row.get("product")):
                    parts.append(f"Item: {row['product']}")
                if pd.notna(row.get("quantity")):
                    parts.append(f"Quantity: {row['quantity']}")
                if pd.notna(row.get("unit_price")):
                    parts.append(f"Unit Price: {row['unit_price']}")
                if pd.notna(row.get("purchase_value")):
                    parts.append(f"Total Cost: {row['purchase_value']}")
                # Include any remaining columns
                known = {"purchase_date", "supplier", "product", "quantity", "unit_price", "purchase_value"}
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
                        report_type=ReportType.PURCHASES,
                        business_domain=BusinessDomain.PURCHASES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"key_values_json": json.dumps(canonical_dict)}
                    ))
        return ReportResult(
            report_type=ReportType.PURCHASES,
            report_name="Purchase Report",
            business_domain=BusinessDomain.PURCHASES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
