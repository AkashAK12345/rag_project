import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["item", "quantity sold", "revenue", "date", "category"]
_SHEET_KEYWORDS = ["sales", "sale", "revenue", "transactions"]


class SalesReport(BaseReport):
    """Parses general sales / revenue reports."""

    @classmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        sheet_bonus = 0.3 if cls._sheet_contains_keywords(df_map, _SHEET_KEYWORDS) else 0.0
        best_col_score = 0.0
        for df in df_map.values():
            norm = cls._normalise_columns(df)
            # Penalise if it looks like an outlet report
            if "outlet" in norm.columns or "branch" in norm.columns:
                continue
            score = cls._columns_present(norm, _REQUIRED_COLS)
            if score > best_col_score:
                best_col_score = score
        return min(1.0, best_col_score * 0.7 + sheet_bonus)

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if any(c in norm.columns for c in ["item", "revenue", "quantity sold"]):
                return
        raise ValueError("Sales report must contain item, quantity sold, or revenue columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("date")):
                    parts.append(f"Sales Date: {row['date']}")
                if pd.notna(row.get("item")):
                    parts.append(f"Item Sold: {row['item']}")
                if pd.notna(row.get("category")):
                    parts.append(f"Category: {row['category']}")
                if pd.notna(row.get("quantity sold")):
                    parts.append(f"Quantity Sold: {row['quantity sold']}")
                if pd.notna(row.get("revenue")):
                    parts.append(f"Revenue: {row['revenue']}")
                known = {"date", "item", "category", "quantity sold", "revenue"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.SALES,
                        business_domain=BusinessDomain.SALES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.SALES,
            report_name="Sales Report",
            business_domain=BusinessDomain.SALES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
