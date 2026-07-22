"""reports/generic_report.py — fallback when no domain parser matches."""

import pandas as pd
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType


class GenericReport(BaseReport):
    """
    Fallback parser. Converts every row across all sheets into a Document
    without domain-specific enrichment. Used when no specialised parser
    scores above MIN_DETECTION_CONFIDENCE.
    """

    @classmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        # Always scores 0.1 — wins only when all domain parsers score lower.
        return 0.1

    def validate(self) -> None:
        if not self.df_map:
            raise ValueError("No data found in the uploaded file.")

    def parse(self) -> ReportResult:
        documents = []
        for sheet_name, df in self.df_map.items():
            df = self._normalise_columns(df)
            for _, row in df.iterrows():
                row_text = "\n".join(
                    f"{col}: {val}" for col, val in row.items() if pd.notna(val)
                )
                if row_text.strip():
                    documents.append(
                        self._make_document(
                            text=row_text,
                            report_type=ReportType.GENERIC,
                            business_domain=BusinessDomain.UNKNOWN,
                            source_file=self.source_file,
                            source_type=self.source_type,
                            sheet=sheet_name,
                        )
                    )

        return ReportResult(
            report_type=ReportType.GENERIC,
            report_name="Generic Report",
            business_domain=BusinessDomain.UNKNOWN,
            documents=documents,
            source_type=self.source_type,
            source_file=self.source_file,
        )
