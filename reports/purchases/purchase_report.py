import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["item", "quantity", "unit price", "total", "supplier", "date"]
_SHEET_KEYWORDS = ["purchase", "purchases", "procurement", "vendor", "po"]


class PurchaseReport(BaseReport):
    """Parses purchase / procurement reports from suppliers."""

    @classmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        sheet_bonus = 0.3 if cls._sheet_contains_keywords(df_map, _SHEET_KEYWORDS) else 0.0
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
            if any(c in norm.columns for c in ["item", "supplier", "total"]):
                return
        raise ValueError("Purchase report must contain item, supplier, and total columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("date")):
                    parts.append(f"Purchase Date: {row['date']}")
                if pd.notna(row.get("supplier")):
                    parts.append(f"Supplier: {row['supplier']}")
                if pd.notna(row.get("item")):
                    parts.append(f"Item: {row['item']}")
                if pd.notna(row.get("quantity")):
                    parts.append(f"Quantity: {row['quantity']}")
                if pd.notna(row.get("unit price")):
                    parts.append(f"Unit Price: {row['unit price']}")
                if pd.notna(row.get("total")):
                    parts.append(f"Total Cost: {row['total']}")
                # Include any remaining columns
                known = {"date", "supplier", "item", "quantity", "unit price", "total"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.PURCHASES,
                        business_domain=BusinessDomain.PURCHASES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.PURCHASES,
            report_name="Purchase Report",
            business_domain=BusinessDomain.PURCHASES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
