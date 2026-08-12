import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class StockReport(BaseReport):
    """Parses current stock level / balance reports."""
    
    BUSINESS_DOMAIN = BusinessDomain.INVENTORY
    REPORT_NAMES = ["Stock Report", "Stock Balance", "Inventory Status"]
    KEYWORDS = ["stock", "balance", "on hand", "inventory status"]
    
    REQUIRED_FIELDS = ["product", "quantity"]
    OPTIONAL_FIELDS = ["reorder level", "value", "location"]
    
    COVERAGE = {
        "metrics": ["total_stock_value", "reorder_count"],
        "charts": ["stock_distribution"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if "item" in norm.columns and any(c in norm.columns for c in ["on hand", "stock", "quantity"]):
                return
        raise ValueError("Stock report must contain item and quantity/on hand columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            
            qty_col = "on hand" if "on hand" in norm.columns else (
                "stock" if "stock" in norm.columns else (
                    "quantity" if "quantity" in norm.columns else None
                )
            )

            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("item")):
                    parts.append(f"Item: {row['item']}")
                if qty_col and pd.notna(row.get(qty_col)):
                    parts.append(f"Stock on Hand: {row[qty_col]}")
                if pd.notna(row.get("reorder level")):
                    parts.append(f"Reorder Level: {row['reorder level']}")
                if pd.notna(row.get("value")):
                    parts.append(f"Total Value: {row['value']}")
                
                known = {"item", "reorder level", "value", qty_col}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.STOCK,
                        business_domain=BusinessDomain.INVENTORY,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.STOCK,
            report_name="Stock Report",
            business_domain=BusinessDomain.INVENTORY,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
