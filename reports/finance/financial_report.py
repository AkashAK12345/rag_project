import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

_REQUIRED_COLS = ["account", "debit", "credit", "balance", "date", "description"]
_SHEET_KEYWORDS = ["finance", "ledger", "pnl", "profit", "loss", "balance sheet", "accounting"]


class FinancialReport(BaseReport):
    """Parses financial, ledger, and P&L reports."""

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
            if any(c in norm.columns for c in ["account", "balance", "debit", "credit"]):
                return
        raise ValueError("Financial report must contain account and balance/debit/credit columns.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            norm = self._normalise_columns(df)
            for _, row in norm.iterrows():
                parts = []
                if pd.notna(row.get("date")):
                    parts.append(f"Date: {row['date']}")
                if pd.notna(row.get("account")):
                    parts.append(f"Account: {row['account']}")
                if pd.notna(row.get("description")):
                    parts.append(f"Description: {row['description']}")
                if pd.notna(row.get("debit")):
                    parts.append(f"Debit: {row['debit']}")
                if pd.notna(row.get("credit")):
                    parts.append(f"Credit: {row['credit']}")
                if pd.notna(row.get("balance")):
                    parts.append(f"Balance: {row['balance']}")
                
                known = {"date", "account", "description", "debit", "credit", "balance"}
                for col, val in row.items():
                    if col not in known and pd.notna(val):
                        parts.append(f"{col.title()}: {val}")
                if parts:
                    documents.append(self._make_document(
                        text="\n".join(parts),
                        report_type=ReportType.FINANCIAL,
                        business_domain=BusinessDomain.FINANCE,
                        source_file=self.source_file,
                        source_type=self.source_type,
                        sheet=sheet_name,
                    ))
        return ReportResult(
            report_type=ReportType.FINANCIAL,
            report_name="Financial Report",
            business_domain=BusinessDomain.FINANCE,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
