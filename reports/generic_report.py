"""reports/generic_report.py — fallback when no domain parser matches."""

import re
import pandas as pd
from core.logging import get_logger
from reports.base_report import BaseReport
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType

logger = get_logger(__name__)

# Fraction of Unnamed: columns that triggers header-row search
_UNNAMED_THRESHOLD = 0.5

# Maximum number of rows to scan when searching for the true header row
_HEADER_SCAN_ROWS = 10

# Fraction of nulls in a column above which an Unnamed: column is dropped
_DROP_NULL_THRESHOLD = 0.8

_UNNAMED_RE = re.compile(r"^unnamed:\s*\d+$", re.IGNORECASE)


class GenericReport(BaseReport):
    """
    Fallback parser. Converts every row across all sheets into a Document
    without domain-specific enrichment. Used when no specialised parser
    scores above MIN_DETECTION_CONFIDENCE.

    Includes a generic preprocessing pipeline that detects actual header
    rows in ERP-style reports where the first few rows are decorative
    titles rather than column headers.
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
            df = self._preprocess_dataframe(df, sheet_name)
            if df is None or df.empty:
                continue
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

    # ------------------------------------------------------------------
    # Generic preprocessing pipeline (no report-specific logic)
    # ------------------------------------------------------------------

    @staticmethod
    def _preprocess_dataframe(
        df: pd.DataFrame,
        sheet_name: str,
    ) -> pd.DataFrame | None:
        """
        Generic heuristic preprocessing for ERP-generated Excel sheets.

        Steps:
        1. Detect whether the auto-assigned header row (row 0) is actually
           a decorative row by counting the fraction of 'Unnamed:' columns.
        2. If unnamed fraction >= threshold, scan the first N rows for the
           best candidate header row (most unique, non-null string values).
        3. Drop columns that are entirely null (formatting artefacts).
        4. Drop remaining Unnamed: columns that have >= 80% null values.
        5. Normalise column names to Title Case for readable document text.

        This is intentionally report-agnostic. It works on any tabular
        Excel export regardless of business domain.

        Args:
            df:         Raw DataFrame as loaded from the source (header=0).
            sheet_name: Name of the sheet (used for logging only).

        Returns:
            Cleaned DataFrame, or None if no meaningful data remains.
        """
        if df.empty:
            return None

        # Step 1: Measure unnamed fraction in the current header
        unnamed_fraction = GenericReport._unnamed_fraction(df)

        if unnamed_fraction >= _UNNAMED_THRESHOLD:
            logger.debug(
                f"GenericReport [{sheet_name}]: {unnamed_fraction:.0%} Unnamed columns — "
                f"scanning for true header row."
            )
            df = GenericReport._detect_header_row(df, sheet_name)
            if df is None or df.empty:
                return None

        # Step 2: Drop entirely-null columns (blank separator columns)
        df = df.dropna(axis=1, how="all")

        # Step 3: Drop Unnamed: columns that are mostly empty
        cols_to_drop = [
            col for col in df.columns
            if _UNNAMED_RE.match(str(col))
            and (df[col].isna().sum() / max(len(df), 1)) >= _DROP_NULL_THRESHOLD
        ]
        if cols_to_drop:
            logger.debug(
                f"GenericReport [{sheet_name}]: dropping {len(cols_to_drop)} "
                f"sparse Unnamed columns: {cols_to_drop}"
            )
            df = df.drop(columns=cols_to_drop)

        # Step 4: Drop rows that are entirely null
        df = df.dropna(how="all")

        if df.empty:
            return None

        # Step 5: Normalise column names to Title Case
        df = df.copy()
        df.columns = [
            GenericReport._normalise_column_name(str(c)) for c in df.columns
        ]

        return df

    @staticmethod
    def _unnamed_fraction(df: pd.DataFrame) -> float:
        """Return the fraction of column names matching the Unnamed: pattern."""
        if df.empty or len(df.columns) == 0:
            return 0.0
        count = sum(1 for c in df.columns if _UNNAMED_RE.match(str(c)))
        return count / len(df.columns)

    @staticmethod
    def _detect_header_row(
        df: pd.DataFrame,
        sheet_name: str,
    ) -> pd.DataFrame | None:
        """
        Scan the first _HEADER_SCAN_ROWS rows of the DataFrame (treated as
        data rows with the current header) and find the row with the most
        unique, non-null string values. Re-assign that row as the header.

        This handles ERP reports where row 0 is a company name or report
        title and the actual column headers are on row 2 or 3.

        Falls back to the original DataFrame if no better row is found.
        """
        scan_limit = min(_HEADER_SCAN_ROWS, len(df))

        best_row_idx: int | None = None
        best_score = 0

        for i in range(scan_limit):
            row_values = df.iloc[i].values
            # Score: count of non-null string cells that are not duplicates
            string_vals = [
                str(v).strip()
                for v in row_values
                if pd.notna(v) and str(v).strip()
            ]
            unique_strings = len(set(string_vals))
            # Penalise rows that are mostly numeric (those are data rows)
            numeric_count = sum(
                1 for v in string_vals
                if re.match(r"^-?\d[\d,\.]*$", v)
            )
            score = unique_strings - numeric_count

            if score > best_score:
                best_score = score
                best_row_idx = i

        if best_row_idx is None or best_score <= 1:
            logger.debug(
                f"GenericReport [{sheet_name}]: no better header row found, "
                f"using original header."
            )
            return df

        # Re-build the DataFrame using the detected header row
        new_header = df.iloc[best_row_idx].values
        new_df = df.iloc[best_row_idx + 1:].copy()
        new_df.columns = [
            str(v).strip() if pd.notna(v) and str(v).strip() else f"Unnamed: {i}"
            for i, v in enumerate(new_header)
        ]
        new_df = new_df.reset_index(drop=True)

        logger.debug(
            f"GenericReport [{sheet_name}]: re-assigned header from row {best_row_idx} "
            f"(score={best_score}). Columns: {list(new_df.columns)}"
        )
        return new_df

    @staticmethod
    def _normalise_column_name(name: str) -> str:
        """
        Convert a raw column name to a clean, human-readable Title Case label.

        Examples:
            'employee_name'  → 'Employee Name'
            'WORK_LOCATION'  → 'Work Location'
            'Unnamed: 3'     → 'Unnamed: 3'  (left as-is for later dropping)
        """
        # Replace underscores and hyphens with spaces
        name = name.replace("_", " ").replace("-", " ")
        # Collapse multiple spaces
        name = re.sub(r"\s+", " ", name).strip()
        # Title-case (preserves Unnamed: prefix for later cleanup step)
        return name.title()
