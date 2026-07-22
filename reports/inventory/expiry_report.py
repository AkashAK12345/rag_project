import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["item", "expiry date", "batch", "quantity"]
_SHEET_KEYWORDS = ["expiry", "expiration", "perishable"]


class ExpiryReport(BaseReport):
    """Parses inventory expiry reports."""

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
            if "expiry date" in norm.columns or "expiration date" in norm.columns:
                return
        raise ValueError("Expiry report must contain an expiry date column.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            
            # Map alternative names
            expiry_col = "expiry date" if "expiry date" in norm.columns else (
                "expiration date" if "expiration date" in norm.columns else None
            )

            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("item")):
                    parts.append(f"Item: {row['item']}")
                if pd.notna(row.get("batch")):
                    parts.append(f"Batch: {row['batch']}")
                if expiry_col and pd.notna(row.get(expiry_col)):
                    parts.append(f"Expiry Date: {row[expiry_col]}")
                if pd.notna(row.get("quantity")):
                    parts.append(f"Quantity: {row['quantity']}")
                
                known = {"item", "batch", "quantity", expiry_col}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.EXPIRY,
                        business_domain=BusinessDomain.INVENTORY,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.EXPIRY,
            report_name="Expiry Report",
            business_domain=BusinessDomain.INVENTORY,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
