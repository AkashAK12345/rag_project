import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class WastageReport(BaseReport):
    """Parses inventory wastage, spoilage, and loss reports."""
    
    BUSINESS_DOMAIN = BusinessDomain.WASTAGE
    REPORT_NAMES = ["Wastage Report", "Spoilage Log", "Loss Report"]
    KEYWORDS = ["wastage", "spoilage", "loss", "damage", "discard"]
    
    REQUIRED_FIELDS = ["product", "quantity", "reason"]
    OPTIONAL_FIELDS = ["transaction_date", "cost", "loss"]
    
    COVERAGE = {
        "metrics": ["total_wastage", "financial_loss"],
        "charts": ["wastage_trend"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if "item" in norm.columns and any(c in norm.columns for c in ["reason", "loss", "spoilage", "wastage"]):
                return
        raise ValueError("Wastage report must contain item and reason/loss columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("date")):
                    parts.append(f"Date: {row['date']}")
                if pd.notna(row.get("item")):
                    parts.append(f"Item: {row['item']}")
                if pd.notna(row.get("quantity")):
                    parts.append(f"Quantity Wasted: {row['quantity']}")
                if pd.notna(row.get("reason")):
                    parts.append(f"Reason: {row['reason']}")
                if pd.notna(row.get("cost")):
                    parts.append(f"Cost of Loss: {row['cost']}")
                if pd.notna(row.get("loss")):
                    parts.append(f"Loss Value: {row['loss']}")
                
                known = {"date", "item", "quantity", "reason", "cost", "loss"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.WASTAGE,
                        business_domain=BusinessDomain.WASTAGE,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.WASTAGE,
            report_name="Wastage Report",
            business_domain=BusinessDomain.WASTAGE,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
