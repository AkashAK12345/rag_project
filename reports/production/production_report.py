import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

class ProductionReport(BaseReport):
    """Parses production line output logs."""
    
    BUSINESS_DOMAIN = BusinessDomain.PRODUCTION
    REPORT_NAMES = ["Production Report", "Manufacturing Log", "Line Output"]
    KEYWORDS = ["production", "manufacturing", "output", "line"]
    
    REQUIRED_FIELDS = ["product", "quantity"]
    OPTIONAL_FIELDS = ["production_date", "machine", "shift"]
    
    COVERAGE = {
        "metrics": ["total_output", "defect_rate"],
        "charts": ["production_trend"]
    }

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if any(c in norm.columns for c in ["recipe", "yield", "produced"]):
                return
        raise ValueError("Production report must contain recipe, yield, or produced columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("date")):
                    parts.append(f"Date: {row['date']}")
                if pd.notna(row.get("recipe")):
                    parts.append(f"Recipe: {row['recipe']}")
                if pd.notna(row.get("item")):
                    parts.append(f"Item: {row['item']}")
                if pd.notna(row.get("produced")):
                    parts.append(f"Produced Quantity: {row['produced']}")
                if pd.notna(row.get("yield")):
                    parts.append(f"Yield: {row['yield']}")
                if pd.notna(row.get("cost")):
                    parts.append(f"Cost: {row['cost']}")
                
                known = {"date", "recipe", "item", "produced", "yield", "cost"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.PRODUCTION,
                        business_domain=BusinessDomain.PRODUCTION,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.PRODUCTION,
            report_name="Production Report",
            business_domain=BusinessDomain.PRODUCTION,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
