"""
reports/base_report.py

Abstract base class for every business report parser.

Responsibilities of every concrete subclass:
  detect()          — score how likely this parser fits the incoming data (0.0–1.0)
  validate()        — raise ValueError if required columns / sheets are missing
  parse()           — build domain-enriched Documents and return a ReportResult
"""

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd

from llama_index.core.schema import Document
from schemas.report import BusinessDomain, ReportResult, ReportType, SourceType
from core.logging import get_logger

logger = get_logger(__name__)

# Confidence threshold: parsers scoring below this yield to the GenericReport
MIN_DETECTION_CONFIDENCE = 0.5


class BaseReport(ABC):
    """
    Contract for all business report parsers.

    Constructor receives:
        df_map      — {sheet_name: pd.DataFrame} produced by a Source
        source_file — original file name (for metadata only)
        source_type — SourceType enum value
    """

    def __init__(
        self,
        df_map: dict[str, pd.DataFrame],
        source_file: str,
        source_type: SourceType,
    ) -> None:
        self.df_map = df_map
        self.source_file = source_file
        self.source_type = source_type

    # ------------------------------------------------------------------
    # Detection (class-level — called before instantiation)
    # ------------------------------------------------------------------

    @classmethod
    @abstractmethod
    def detect(cls, df_map: dict[str, pd.DataFrame]) -> float:
        """
        Score how well this parser matches the incoming data.

        Args:
            df_map: {sheet_name: DataFrame} produced by a Source.

        Returns:
            Confidence in [0.0, 1.0].
            0.0  = definitely not this report type
            1.0  = exact match (e.g., all required columns found)
        """
        ...

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @abstractmethod
    def validate(self) -> None:
        """
        Raise ValueError if required columns or sheets are missing.
        Called by IngestionService before parse() to surface 422-class errors.
        """
        ...

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @abstractmethod
    def parse(self) -> ReportResult:
        """
        Build domain-enriched LlamaIndex Documents and wrap them in a
        ReportResult. This is where all business understanding lives.
        """
        ...

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Strip whitespace and lower-case column names for comparison."""
        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df

    @staticmethod
    def _columns_present(df: pd.DataFrame, required: list[str]) -> float:
        """
        Return the fraction of required column names found in df (case-insensitive).
        Used to compute detect() confidence scores.
        """
        if df.empty or not required:
            return 0.0
        present = [c for c in required if c in df.columns]
        return len(present) / len(required)

    @staticmethod
    def _sheet_contains_keywords(
        df_map: dict[str, pd.DataFrame], keywords: list[str]
    ) -> bool:
        """
        True if any sheet name contains at least one of the given keywords.
        Sheet names are compared case-insensitively.
        """
        lower_sheets = {k.lower(): k for k in df_map}
        return any(
            any(kw in sheet for sheet in lower_sheets) for kw in keywords
        )

    @staticmethod
    def _make_document(
        text: str,
        report_type: ReportType,
        business_domain: BusinessDomain,
        source_file: str,
        source_type: SourceType,
        sheet: str,
        extra: dict[str, Any] | None = None,
    ) -> Document:
        """Construct a LlamaIndex Document with consistent enterprise metadata."""
        metadata: dict[str, Any] = {
            "report_type": report_type.value,
            "business_domain": business_domain.value,
            "source_file": source_file,
            "source_type": source_type.value,
            "sheet": sheet,
        }
        if extra:
            metadata.update(extra)
        return Document(text=text, metadata=metadata)
