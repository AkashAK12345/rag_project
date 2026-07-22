"""
schemas/reasoning_context.py

Output schema of BusinessReasoningService.

ReasoningContext is the fully reasoned, cross-domain enriched input that
RagService uses to construct the final LLM prompt. It is strictly richer
than BusinessContext — it adds relationships, risks, and opportunities
derived through reasoning, not just retrieval.

Design decision: plain dataclasses. No FastAPI, no SQLAlchemy, no LlamaIndex.
LangGraph agents in future milestones can inspect each field independently
to decide whether to re-plan, re-retrieve, or generate.
"""

from dataclasses import dataclass, field
from schemas.report import BusinessDomain
from schemas.business_insight import BusinessInsight, InsightSeverity
from schemas.query_context import BusinessContext


@dataclass
class CrossDomainRelationship:
    """
    A detected directional relationship between two business domains.

    Examples:
      "Supplier price increase (Purchases) → Higher food cost (Finance)"
      "Low inventory (Inventory) → Reduced outlet revenue (Sales)"

    Fields:
        from_domain     — the domain where the causal signal originates
        to_domain       — the domain that is affected
        relationship    — human-readable description of the link
        confidence      — estimated confidence in the relationship [0.0–1.0]
        supporting_data — evidence keys that support this relationship
    """
    from_domain: BusinessDomain
    to_domain: BusinessDomain
    relationship: str
    confidence: float = 0.5
    supporting_data: list[str] = field(default_factory=list)


@dataclass
class DetectedRisk:
    """A business risk identified through cross-domain reasoning."""
    domain: BusinessDomain
    description: str
    severity: InsightSeverity
    related_domains: list[BusinessDomain] = field(default_factory=list)


@dataclass
class DetectedOpportunity:
    """A positive signal or actionable opportunity identified through reasoning."""
    domain: BusinessDomain
    description: str
    related_domains: list[BusinessDomain] = field(default_factory=list)


@dataclass
class ReasoningContext:
    """
    The complete output of BusinessReasoningService.

    Contains everything RagService needs to construct an intelligent,
    cross-domain-aware LLM prompt.

    Fields:
        source_context      — the original BusinessContext (for provenance)
        insights            — derived business insights from InsightBuilder
        relationships       — detected cross-domain causal relationships
        risks               — identified risks from cross-domain reasoning
        opportunities       — identified opportunities from cross-domain reasoning
        overall_confidence  — blended confidence across all reasoning steps
        reasoning_text      — pre-formatted reasoning summary for the LLM prompt
    """
    source_context: BusinessContext
    insights: list[BusinessInsight] = field(default_factory=list)
    relationships: list[CrossDomainRelationship] = field(default_factory=list)
    risks: list[DetectedRisk] = field(default_factory=list)
    opportunities: list[DetectedOpportunity] = field(default_factory=list)
    overall_confidence: float = 0.5
    reasoning_text: str = ""
