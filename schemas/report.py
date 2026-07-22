"""
schemas/report.py

Pure Python data structures shared across the entire ingestion pipeline.

Design decision: these are plain dataclasses (not Pydantic models) because
they are never serialised to JSON inside the pipeline itself. Keeping them
as dataclasses means zero dependency on FastAPI, SQLAlchemy, or LlamaIndex —
the Report Framework stays portable and independently testable.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from llama_index.core.schema import Document


class BusinessDomain(str, Enum):
    SALES = "sales"
    INVENTORY = "inventory"
    PURCHASES = "purchases"
    FINANCE = "finance"
    EMPLOYEES = "employees"
    PRODUCTION = "production"
    WASTAGE = "wastage"
    UNKNOWN = "unknown"


class ReportType(str, Enum):
    # Sales
    SALES = "sales_report"
    OUTLET_SALES = "outlet_sales_report"
    # Inventory
    INVENTORY = "inventory_report"
    EXPIRY = "expiry_report"
    STOCK = "stock_report"
    # Purchases
    PURCHASES = "purchase_report"
    # Finance
    FINANCIAL = "financial_report"
    # Employees
    ATTENDANCE = "attendance_report"
    EMPLOYEE = "employee_report"
    # Production
    PRODUCTION = "production_report"
    # Wastage
    WASTAGE = "wastage_report"
    # Fallback
    GENERIC = "generic_report"


class SourceType(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    # Future
    SQL = "sql"
    API = "api"
    WEBSITE = "website"
    POS = "pos"


@dataclass
class ReportResult:
    """
    The canonical output of every report parser.

    Design decision: IndexingService consumes ReportResult.documents and
    ReportResult.metadata. It never needs to know the source type, the
    file format, or how the documents were created. This is the Anti-Corruption
    Layer between business intelligence and the vector store.
    """
    report_type: ReportType
    report_name: str
    business_domain: BusinessDomain
    documents: list[Document]
    source_type: SourceType
    source_file: str

    # Optional enterprise metadata
    organization_id: str | None = None
    reporting_period: str | None = None
    imported_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"
    extra_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def document_count(self) -> int:
        return len(self.documents)
