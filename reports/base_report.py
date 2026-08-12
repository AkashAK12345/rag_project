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

    # Capability Metadata (to be overridden by subclasses)
    BUSINESS_DOMAIN: BusinessDomain = BusinessDomain.UNKNOWN
    REPORT_NAMES: list[str] = []
    KEYWORDS: list[str] = []
    REQUIRED_FIELDS: list[str] = []
    OPTIONAL_FIELDS: list[str] = []
    COVERAGE: dict[str, list[str]] = {"metrics": [], "charts": []}

    # ------------------------------------------------------------------
    # Universal Detection Engine
    # ------------------------------------------------------------------

    @classmethod
    def evaluate_sheet_confidence(cls, sheet_name: str, df: pd.DataFrame) -> Any:
        from schemas.report import DetectionDiagnostic
        
        norm_df = cls._normalise_columns(df)
        columns = [str(c) for c in norm_df.columns]
        
        matched_required = [req for req in cls.REQUIRED_FIELDS if any(req in c for c in columns)]
        missing_required = [req for req in cls.REQUIRED_FIELDS if req not in matched_required]
        
        matched_optional = [opt for opt in cls.OPTIONAL_FIELDS if any(opt in c for c in columns)]
        missing_optional = [opt for opt in cls.OPTIONAL_FIELDS if opt not in matched_optional]
        
        sheet_matched = any(kw.lower() in sheet_name.lower() for kw in cls.KEYWORDS)
        
        # A parser is strictly accepted if all required fields are present.
        accepted = (len(missing_required) == 0) if cls.REQUIRED_FIELDS else False
        
        req_score = len(matched_required) / max(len(cls.REQUIRED_FIELDS), 1)
        opt_score = len(matched_optional) / max(len(cls.OPTIONAL_FIELDS), 1)
        sheet_score = 1.0 if sheet_matched else 0.0
        
        score = (req_score * 0.5) + (opt_score * 0.3) + (sheet_score * 0.2)
        
        return DetectionDiagnostic(
            parser_name=cls.__name__,
            matched_required=matched_required,
            missing_required=missing_required,
            matched_optional=matched_optional,
            missing_optional=missing_optional,
            sheet_matched=sheet_matched,
            score=score,
            accepted=accepted
        )

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
        """Standardize column names using FieldNormalizationService."""
        from services.field_normalization_service import FieldNormalizationService
        df = df.copy()
        df.columns = [FieldNormalizationService.normalize_column_name(c) for c in df.columns]
        return df

    @staticmethod
    def _columns_present(df: pd.DataFrame, required: list[str]) -> float:
        """
        Return the fraction of required column substrings found in df (case-insensitive).
        Used to compute detect() confidence scores.
        """
        if df.empty or not required:
            return 0.0
        
        present = []
        for req in required:
            # Substring match: if req is inside any column name
            if any(req in c for c in df.columns):
                present.append(req)
                
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
