"""
schemas/connector_result.py

Standardized output from any data source or enterprise connector.

This object acts as the universal input to the IngestionService, completely
decoupling business report parsing from data acquisition methods.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import pandas as pd
from typing import Any

from schemas.report import SourceType


@dataclass
class ConnectorResult:
    """
    The canonical payload containing fetched enterprise data.

    Fields:
        source_type:     What kind of system produced this (EXCEL, SQL, REST)
        organization_id: Enterprise multi-tenancy context
        dataset_name:    Logical name for this batch (e.g., "DailySales", "upload_01.xlsx")
        dataframes:      Dict mapping logical partition names (tables/sheets/endpoints) to pandas DataFrames
        connector_id:    Optional ID of the configured connector that ran (None for manual file uploads)
        record_count:    Total rows retrieved across all dataframes
        retrieved_at:    Timestamp of the fetch completion
        warnings:        Non-fatal issues encountered during fetch (e.g., pagination timeouts)
        errors:          Fatal issues encountered, if any (usually raises exception, but can be collected)
        metadata:        Additional context (e.g., query used, URL fetched)
    """
    source_type: SourceType
    dataset_name: str
    dataframes: dict[str, pd.DataFrame]
    
    organization_id: str | None = None
    connector_id: str | None = None
    record_count: int = 0
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Auto-calculate record count if not explicitly set
        if self.record_count == 0 and self.dataframes:
            self.record_count = sum(len(df) for df in self.dataframes.values())
