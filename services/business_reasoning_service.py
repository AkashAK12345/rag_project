"""
services/business_reasoning_service.py

Transforms a structured BusinessContext into a ReasoningContext by
identifying cross-domain relationships, risks, and opportunities.

Responsibilities:
  - Collect all BusinessObservation objects from BusinessContext.sections.
  - Delegate to InsightBuilder for insight derivation.
  - Detect cross-domain relationships between active domains.
  - Classify risks and opportunities from insights.
  - Assemble the final reasoning_text for RagService.
  - Return a ReasoningContext.

Design rules:
  - NEVER calls the LLM.
  - NEVER reads files or queries the vector store.
  - NEVER knows about the source of the documents.
  - Depends only on in-memory Python data structures.
  - All collaborators are instantiated internally (InsightBuilder is stateless).
  - Independently unit-testable with mock BusinessContext objects.

Why not call the LLM here?
  Calling the LLM to perform reasoning would couple two responsibilities
  (reasoning + generation) in one place. The reasoning layer determines WHAT
  the context means. RagService determines HOW to present it to the user.
  Keeping them separate means reasoning can be retried, cached, or augmented
  by LangGraph agents without affecting generation logic.
"""

from core.logging import get_logger
from services.insight_builder import InsightBuilder, _CAUSAL_CHAINS
from schemas.query_context import BusinessContext, BusinessObservation
from schemas.business_insight import BusinessInsight, InsightSeverity, InsightType
from schemas.reasoning_context import (
    CrossDomainRelationship,
    DetectedOpportunity,
    DetectedRisk,
    ReasoningContext,
)
from schemas.report import BusinessDomain
from schemas.retrieval_plan import QueryType

logger = get_logger(__name__)

# Query types that should always trigger cross-domain reasoning
_REASONING_QUERY_TYPES = {
    QueryType.ROOT_CAUSE,
    QueryType.EXPLAIN,
    QueryType.RECOMMENDATION,
    QueryType.ANOMALY,
    QueryType.TREND,
}

# Severity → label for text rendering
_SEVERITY_LABELS = {
    InsightSeverity.CRITICAL: "⚠️  CRITICAL",
    InsightSeverity.WARNING: "⚡ WARNING",
    InsightSeverity.INFO: "ℹ️  INFO",
    InsightSeverity.POSITIVE: "✅ POSITIVE",
}

# Human-readable domain labels (duplicated to avoid circular import from context_builder)
_DOMAIN_LABELS = {
    BusinessDomain.SALES: "Sales & Revenue",
    BusinessDomain.PURCHASES: "Purchases & Procurement",
    BusinessDomain.INVENTORY: "Inventory & Stock",
    BusinessDomain.FINANCE: "Finance & Accounting",
    BusinessDomain.EMPLOYEES: "Human Resources & Attendance",
    BusinessDomain.PRODUCTION: "Production & Kitchen Operations",
    BusinessDomain.WASTAGE: "Wastage & Loss",
    BusinessDomain.UNKNOWN: "General Business Data",
}


class BusinessReasoningService:
    """
    Produces a ReasoningContext from a BusinessContext.

    The reasoning engine runs in two modes:
      1. Full cross-domain reasoning — for ROOT_CAUSE, EXPLAIN, RECOMMENDATION,
         ANOMALY, and TREND queries. Activates InsightBuilder and relationship detection.
      2. Lightweight pass-through — for LOOKUP and SUMMARIZE queries where
         cross-domain reasoning adds latency without significant value.
         Still produces a ReasoningContext (with fewer insights) for API consistency.
    """

    def __init__(self) -> None:
        self._insight_builder = InsightBuilder()

    def reason(self, business_context: BusinessContext) -> ReasoningContext:
        """
        Analyze the BusinessContext and produce a ReasoningContext.

        Args:
            business_context: Structured context from BusinessContextBuilder.

        Returns:
            A ReasoningContext ready for RagService.generate_response().
        """
        plan = business_context.plan
        query_type = plan.query_type

        logger.info(
            f"BusinessReasoningService: starting reasoning for "
            f"query_type={query_type.value}, domains={[d.value for d in plan.domains]}"
        )

        # Collect all observations across domains
        all_observations: list[BusinessObservation] = []
        for section in business_context.sections:
            all_observations.extend(section.observations)

        logger.info(
            f"BusinessReasoningService: {len(all_observations)} total observation(s) "
            f"from {len(business_context.sections)} domain section(s)."
        )

        # Decide depth of reasoning
        full_reasoning = query_type in _REASONING_QUERY_TYPES

        # Step 1: Build insights
        insights: list[BusinessInsight] = (
            self._insight_builder.build(all_observations)
            if all_observations
            else []
        )

        # Step 2: Detect cross-domain relationships (full reasoning only)
        present_domains = {s.domain for s in business_context.sections}
        relationships: list[CrossDomainRelationship] = []

        if full_reasoning:
            relationships = self._detect_relationships(present_domains, insights)

        # Step 3: Classify risks and opportunities from insights
        risks: list[DetectedRisk] = []
        opportunities: list[DetectedOpportunity] = []

        for insight in insights:
            if insight.severity in (InsightSeverity.CRITICAL, InsightSeverity.WARNING):
                risks.append(DetectedRisk(
                    domain=insight.domain,
                    description=insight.headline,
                    severity=insight.severity,
                    related_domains=insight.related_domains,
                ))
            elif insight.severity == InsightSeverity.POSITIVE:
                opportunities.append(DetectedOpportunity(
                    domain=insight.domain,
                    description=insight.headline,
                    related_domains=insight.related_domains,
                ))

        # Step 4: Compute overall confidence
        overall_confidence = self._compute_confidence(plan.confidence, insights, relationships)

        # Step 5: Assemble reasoning_text
        reasoning_text = self._assemble_reasoning_text(
            business_context=business_context,
            insights=insights,
            relationships=relationships,
            risks=risks,
            opportunities=opportunities,
            query_type=query_type,
        )

        reasoning_context = ReasoningContext(
            source_context=business_context,
            insights=insights,
            relationships=relationships,
            risks=risks,
            opportunities=opportunities,
            overall_confidence=overall_confidence,
            reasoning_text=reasoning_text,
        )

        logger.info(
            f"BusinessReasoningService: complete — "
            f"{len(insights)} insight(s), "
            f"{len(relationships)} relationship(s), "
            f"{len(risks)} risk(s), "
            f"{len(opportunities)} opportunity(ies), "
            f"confidence={overall_confidence:.3f}"
        )

        return reasoning_context

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect_relationships(
        self,
        present_domains: set[BusinessDomain],
        insights: list[BusinessInsight],
    ) -> list[CrossDomainRelationship]:
        """
        Match active domains against the known causal chain catalog.
        Only emits a relationship if both endpoint domains have data present.
        Confidence is raised if both endpoints also have active risk insights.
        """
        domains_with_risk = {
            i.domain for i in insights
            if i.severity in (InsightSeverity.CRITICAL, InsightSeverity.WARNING)
        }

        relationships: list[CrossDomainRelationship] = []
        for from_domain, to_domain, description in _CAUSAL_CHAINS:
            if from_domain in present_domains and to_domain in present_domains:
                both_risky = (from_domain in domains_with_risk
                              and to_domain in domains_with_risk)
                confidence = 0.85 if both_risky else 0.55

                relationships.append(CrossDomainRelationship(
                    from_domain=from_domain,
                    to_domain=to_domain,
                    relationship=description,
                    confidence=confidence,
                    supporting_data=[
                        f"{from_domain.value} data present",
                        f"{to_domain.value} data present",
                        *(["Both domains show risk signals."] if both_risky else []),
                    ],
                ))
        return relationships

    @staticmethod
    def _compute_confidence(
        plan_confidence: float,
        insights: list[BusinessInsight],
        relationships: list[CrossDomainRelationship],
    ) -> float:
        """
        Blended confidence score:
          - Starts from plan.confidence (retrieval quality).
          - Boosts for cross-domain relationships found.
          - Slight penalty when zero insights were generated (data may be sparse).
        """
        base = plan_confidence
        relationship_bonus = min(0.15, len(relationships) * 0.03)
        insight_penalty = -0.1 if not insights else 0.0
        return round(min(1.0, max(0.0, base + relationship_bonus + insight_penalty)), 3)

    def _assemble_reasoning_text(
        self,
        business_context: BusinessContext,
        insights: list[BusinessInsight],
        relationships: list[CrossDomainRelationship],
        risks: list[DetectedRisk],
        opportunities: list[DetectedOpportunity],
        query_type: QueryType,
    ) -> str:
        """
        Build the reasoning summary block injected above the raw context
        in the final LLM prompt. This narrates the AI's pre-reasoning so
        the LLM can focus on answering rather than re-discovering patterns.
        """
        lines: list[str] = []

        # --- Header ---
        lines.append("=== BUSINESS REASONING ANALYSIS ===")
        lines.append(
            f"Query Type: {query_type.value.replace('_', ' ').title()}  |  "
            f"Domains Analyzed: {len(business_context.sections)}  |  "
            f"Observations: {sum(len(s.observations) for s in business_context.sections)}"
        )
        lines.append("")

        # --- Risks ---
        if risks:
            lines.append("IDENTIFIED RISKS:")
            for risk in risks[:5]:
                label = _SEVERITY_LABELS.get(risk.severity, "NOTICE")
                domain_label = _DOMAIN_LABELS.get(risk.domain, risk.domain.value)
                lines.append(f"  {label} [{domain_label}] {risk.description}")
            lines.append("")

        # --- Opportunities ---
        if opportunities:
            lines.append("IDENTIFIED OPPORTUNITIES:")
            for opp in opportunities[:3]:
                domain_label = _DOMAIN_LABELS.get(opp.domain, opp.domain.value)
                lines.append(f"  ✅ POSITIVE [{domain_label}] {opp.description}")
            lines.append("")

        # --- Cross-domain relationships ---
        if relationships:
            lines.append("CROSS-DOMAIN RELATIONSHIPS DETECTED:")
            for rel in relationships:
                from_label = _DOMAIN_LABELS.get(rel.from_domain, rel.from_domain.value)
                to_label = _DOMAIN_LABELS.get(rel.to_domain, rel.to_domain.value)
                conf_pct = int(rel.confidence * 100)
                lines.append(
                    f"  [{from_label}] → [{to_label}]  ({conf_pct}% confidence)"
                )
                lines.append(f"     {rel.relationship}")
            lines.append("")

        # --- Insights summary ---
        cross_domain_insights = [
            i for i in insights if i.insight_type == InsightType.CROSS_DOMAIN_CORRELATION
        ]
        domain_insights = [
            i for i in insights if i.insight_type != InsightType.CROSS_DOMAIN_CORRELATION
        ]

        if domain_insights:
            lines.append("DOMAIN-LEVEL SIGNALS:")
            for insight in domain_insights[:6]:
                domain_label = _DOMAIN_LABELS.get(insight.domain, insight.domain.value)
                lines.append(f"  • [{domain_label}] {insight.headline}")
            lines.append("")

        # Append raw business data context
        lines.append("=== RETRIEVED BUSINESS DATA ===")
        lines.append(business_context.context_text)
        lines.append("")
        lines.append("=== END OF REASONING CONTEXT ===")

        return "\n".join(lines)
