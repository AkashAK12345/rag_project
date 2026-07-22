from pydantic import BaseModel, Field
from schemas.report import ReportType, BusinessDomain, SourceType


class IngestionResponse(BaseModel):
    """Response DTO returned by POST /api/v1/ingest."""
    filename: str
    report_type: ReportType
    report_name: str
    business_domain: BusinessDomain
    source_type: SourceType
    document_count: int
    reporting_period: str | None = None
    message: str
