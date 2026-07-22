import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["item", "quantity", "reason", "date", "cost", "loss"]
_SHEET_KEYWORDS = ["wastage", "spoilage", "loss", "damage", "discard"]


class WastageReport(BaseReport):
    """Parses inventory wastage, spoilage, and loss reports."""

    @classmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        sheet_bonus = 0.4 if cls._sheet_contains_keywords(df_map, _SHEET_KEYWORDS) else 0.0
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
