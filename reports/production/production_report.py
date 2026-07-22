import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["recipe", "item", "yield", "cost", "date", "produced"]
_SHEET_KEYWORDS = ["production", "recipe", "yield", "manufacturing"]


class ProductionReport(BaseReport):
    """Parses kitchen production and recipe yield reports."""

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
