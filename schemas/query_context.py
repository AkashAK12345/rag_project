"""
schemas/query_context.py

Structured outputs of BusinessContextBuilder and related observation types.

BusinessObservation — a factual extraction from a single document node
DomainSection       — all retrieved excerpts + observations for one business domain
BusinessContext     — the full structured context ready for BusinessReasoningService
"""

from dataclasses import dataclass, field
from schemas.report import BusinessDomain
from schemas.retrieval_plan import RetrievalPlan


@dataclass
class BusinessObservation:
    """
    A single factual observation extracted from one retrieved document node.

    InsightBuilder reads a list of these observations (grouped by domain)
    and infers cross-domain relationships and business insights.

    Design decision: observations are extracted here, not in ReasoningService,
    because the ContextBuilder already has access to the raw node metadata.
    Keeping extraction in one place avoids double-parsing.

    Fields:
        domain          — business domain this observation belongs to
        report_type     — the specific report that produced this record
        source_file     — the file the node came from (provenance)
        sheet           — sheet name within the file, if applicable
        key_values      — dict of extracted column → value pairs from the node text
        raw_text        — truncated original node text for fallback
        relevance_score — semantic similarity score from the retriever
    """
    domain: BusinessDomain
    report_type: str
    source_file: str
    sheet: str
    key_values: dict[str, str]    # e.g. {"revenue": "10000", "outlet": "HQ"}
    raw_text: str
    relevance_score: float = 0.0


@dataclass
class DomainSection:
    """
    A coherent block of business evidence from a single domain.

    formatted_text is the human-readable context string for the LLM prompt.
    observations is the structured list consumed by BusinessReasoningService.
    Both are populated by BusinessContextBuilder.
    """
    domain: BusinessDomain
    document_count: int
    formatted_text: str
    observations: list[BusinessObservation] = field(default_factory=list)


@dataclass
class BusinessContext:
    """
    Fully assembled, structured context produced by BusinessContextBuilder.

    Passed to BusinessReasoningService for cross-domain reasoning.
    context_text is the LLM-ready string for RagService.

    Fields:
        plan            — the plan that drove this retrieval (for logging / agents)
        sections        — domain-specific evidence blocks, ordered by relevance
        total_documents — total nodes retrieved across all domains
        context_text    — final assembled prompt string
    """
    plan: RetrievalPlan
    sections: list[DomainSection] = field(default_factory=list)
    total_documents: int = 0
    context_text: str = ""
