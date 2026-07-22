import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["outlet", "revenue", "date", "transactions"]
_SHEET_KEYWORDS = ["outlet", "branch", "location", "store"]


class OutletSalesReport(BaseReport):
    """Parses multi-outlet / branch-level sales performance reports."""

    @classmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        sheet_bonus = 0.35 if cls._sheet_contains_keywords(df_map, _SHEET_KEYWORDS) else 0.0
        best_col_score = 0.0
        for df in df_map.values():
            norm = cls._normalise_columns(df)
            # Outlet/branch column is a strong signal
            outlet_bonus = 0.2 if ("outlet" in norm.columns or "branch" in norm.columns) else 0.0
            score = cls._columns_present(norm, _REQUIRED_COLS) * 0.7 + outlet_bonus
            if score > best_col_score:
                best_col_score = score
        return min(1.0, best_col_score + sheet_bonus)

    def validate(self) -> None:
        for df in self.df_map.values():
            norm = self._normalise_columns(df)
            if "outlet" in norm.columns or "branch" in norm.columns:
                return
        raise ValueError("Outlet sales report must contain an 'outlet' or 'branch' column.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                outlet = row.get("outlet") or row.get("branch")
                if pd.notna(outlet):
                    parts.append(f"Outlet: {outlet}")
                if pd.notna(row.get("date")):
                    parts.append(f"Date: {row['date']}")
                if pd.notna(row.get("revenue")):
                    parts.append(f"Revenue: {row['revenue']}")
                if pd.notna(row.get("transactions")):
                    parts.append(f"Transactions: {row['transactions']}")
                known = {"outlet", "branch", "date", "revenue", "transactions"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.OUTLET_SALES,
                        business_domain=BusinessDomain.SALES,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                        extra={"outlet": str(outlet) if pd.notna(outlet) else None},
                    ))
        return ReportResult(
            report_type=ReportType.OUTLET_SALES,
            report_name="Outlet Sales Report",
            business_domain=BusinessDomain.SALES,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
