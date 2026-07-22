"""
services/context_builder.py

BusinessContextBuilder transforms a ranked list of retrieved document nodes
into a structured, domain-organized context block that the LLM can read as
a coherent business briefing.

This is NOT simple chunk concatenation.

The builder:
  1. Groups nodes by business_domain metadata.
  2. Applies intent-aware narration: different query types get different
     framing around the evidence.
  3. Adds a context header summarising what data is available.
  4. Orders sections by domain relevance (using the plan's domain list).
  5. Extracts BusinessObservation objects per node for BusinessReasoningService.
  6. Produces structured business summaries (revenue, top entities, stock signals)
     in addition to the raw evidence.
  7. Produces a self-contained context_text string injected into the prompt.

Design principle: all formatting decisions live here, not in RagService or
the API layer. When LangGraph agents need to inspect individual sections,
they can read BusinessContext.sections without parsing the assembled string.
"""

import re
from collections import defaultdict

from core.logging import get_logger
from schemas.query_context import BusinessContext, BusinessObservation, DomainSection
from schemas.retrieval_plan import QueryIntent, QueryType, RetrievalPlan
from schemas.report import BusinessDomain

logger = get_logger(__name__)

# Maximum characters per retrieved node included in context (avoids prompt bloat)
MAX_NODE_LENGTH = 400

# Pattern to extract key: value pairs from node text
_KV_RE = re.compile(r"([A-Za-z ]+):\s*(.+?)(?:\n|$)")

# Intent-aware section headers
_QUERY_TYPE_HEADERS: dict[QueryType, str] = {
    QueryType.COMPARE: "COMPARATIVE ANALYSIS CONTEXT",
    QueryType.TREND: "TREND ANALYSIS CONTEXT",
    QueryType.ANOMALY: "ANOMALY INVESTIGATION CONTEXT",
    QueryType.EXPLAIN: "ROOT CAUSE ANALYSIS CONTEXT",
    QueryType.RECOMMENDATION: "RECOMMENDATION CONTEXT",
    QueryType.SUMMARIZE: "SUMMARY CONTEXT",
    QueryType.LOOKUP: "DATA LOOKUP CONTEXT",
    QueryType.ROOT_CAUSE: "ROOT CAUSE ANALYSIS CONTEXT",
}

# Intent-specific instructions embedded in context for the LLM
_INTENT_INSTRUCTIONS: dict[QueryIntent, str] = {
    QueryIntent.COMPARE_ENTITIES:
        "Focus on differences and similarities between the entities in the data below.",
    QueryIntent.IDENTIFY_TOP_PERFORMER:
        "Identify the highest-performing entity from the data below.",
    QueryIntent.IDENTIFY_BOTTOM_PERFORMER:
        "Identify the lowest-performing entity from the data below.",
    QueryIntent.IDENTIFY_TREND:
        "Identify patterns and directional changes over time from the data below.",
    QueryIntent.IDENTIFY_ANOMALY:
        "Look for values that are unusual, unexpected, or significantly deviate from the norm.",
    QueryIntent.EXPLAIN_CAUSE:
        "Analyze the data below to explain the root cause of the situation.",
    QueryIntent.REQUEST_RECOMMENDATION:
        "Based on the data below, provide concrete, actionable recommendations.",
    QueryIntent.SUMMARIZE_REPORT:
        "Provide a comprehensive summary of the key figures and insights from the data below.",
    QueryIntent.LOOKUP_VALUE:
        "Locate and report the specific value requested from the data below.",
    QueryIntent.GENERAL:
        "Answer the question using the business data provided below.",
}

# Human-readable domain display names
_DOMAIN_LABELS: dict[BusinessDomain, str] = {
    BusinessDomain.SALES: "Sales & Revenue",
    BusinessDomain.PURCHASES: "Purchases & Procurement",
    BusinessDomain.INVENTORY: "Inventory & Stock",
    BusinessDomain.FINANCE: "Finance & Accounting",
    BusinessDomain.EMPLOYEES: "Human Resources & Attendance",
    BusinessDomain.PRODUCTION: "Production & Kitchen Operations",
    BusinessDomain.WASTAGE: "Wastage & Loss",
    BusinessDomain.UNKNOWN: "General Business Data",
}

# Domain-specific summary field hints — keys to look for in node text
_DOMAIN_SUMMARY_HINTS: dict[BusinessDomain, list[str]] = {
    BusinessDomain.SALES: ["revenue", "total sales", "transactions", "outlet", "top item"],
    BusinessDomain.PURCHASES: ["supplier", "total cost", "price", "vendor", "amount"],
    BusinessDomain.INVENTORY: ["item", "on hand", "reorder level", "quantity", "value"],
    BusinessDomain.FINANCE: ["account", "balance", "debit", "credit", "profit"],
    BusinessDomain.EMPLOYEES: ["employee", "hours", "attendance", "status", "role"],
    BusinessDomain.PRODUCTION: ["recipe", "yield", "produced", "cost", "batch"],
    BusinessDomain.WASTAGE: ["item", "quantity wasted", "reason", "loss value", "cost of loss"],
}


class BusinessContextBuilder:
    """
    Transforms ranked retrieval results into a structured business context.

    Usage:
        builder = BusinessContextBuilder()
        context = builder.build(nodes, plan)
        # context.context_text is ready for the LLM prompt
        # context.sections[i].observations is ready for BusinessReasoningService
    """

    def build(self, nodes: list, plan: RetrievalPlan) -> BusinessContext:
        """
        Build a BusinessContext from retrieved nodes and the active plan.

        Args:
            nodes: List of LlamaIndex NodeWithScore objects from RetrievalService.
            plan:  The RetrievalPlan that drove this retrieval.

        Returns:
            A BusinessContext with fully assembled context_text and structured observations.
        """
        if not nodes:
            logger.warning("BusinessContextBuilder: received zero nodes.")
            return BusinessContext(
                plan=plan,
                sections=[],
                total_documents=0,
                context_text="No relevant business data found for this query.",
            )

        # Step 1: Group nodes by business_domain
        domain_buckets: dict[BusinessDomain, list] = defaultdict(list)
        for node_with_score in nodes:
            node = getattr(node_with_score, "node", None)
            if not node:
                continue
            metadata = getattr(node, "metadata", {})
            domain_raw = metadata.get("business_domain", BusinessDomain.UNKNOWN.value)
            try:
                domain = BusinessDomain(domain_raw)
            except ValueError:
                domain = BusinessDomain.UNKNOWN
            domain_buckets[domain].append(node_with_score)

        # Step 2: Order sections by plan.domains priority, then remaining
        ordered_domains = list(plan.domains)
        for domain in domain_buckets:
            if domain not in ordered_domains:
                ordered_domains.append(domain)

        # Step 3: Build DomainSection objects (with observations)
        sections: list[DomainSection] = []
        for domain in ordered_domains:
            bucket = domain_buckets.get(domain)
            if not bucket:
                continue
            section = self._build_section(domain, bucket)
            sections.append(section)

        # Step 4: Assemble full context text
        context_text = self._assemble_context(sections, plan)

        context = BusinessContext(
            plan=plan,
            sections=sections,
            total_documents=len(nodes),
            context_text=context_text,
        )

        logger.info(
            f"BusinessContextBuilder: built context with {len(sections)} domain section(s), "
            f"{len(nodes)} total document(s), "
            f"{sum(len(s.observations) for s in sections)} observation(s)."
        )
        return context

    # ------------------------------------------------------------------
    # Private builders
    # ------------------------------------------------------------------

    def _build_section(self, domain: BusinessDomain, nodes: list) -> DomainSection:
        """
        Build a single domain section from its relevant nodes.
        Extracts BusinessObservation objects alongside formatted text.
        """
        lines: list[str] = []
        observations: list[BusinessObservation] = []
        summary_hints = _DOMAIN_SUMMARY_HINTS.get(domain, [])

        for idx, node_with_score in enumerate(nodes, start=1):
            node = getattr(node_with_score, "node", None)
            if not node:
                continue

            text: str = getattr(node, "text", "")
            metadata: dict = getattr(node, "metadata", {})
            score: float = getattr(node_with_score, "score", 0.0) or 0.0

            # Truncate for prompt safety
            display_text = text[:MAX_NODE_LENGTH].rstrip() + "..." if len(text) > MAX_NODE_LENGTH else text

            source_file = metadata.get("source_file", "")
            sheet = metadata.get("sheet", "")
            report_type = metadata.get("report_type", "")

            # Provenance annotation
            provenance_parts = [p for p in [source_file, sheet, report_type] if p]
            provenance = f"[Source: {' | '.join(provenance_parts)}]" if provenance_parts else ""

            lines.append(f"  [{idx}] {provenance}\n      {display_text}")

            # --- Extract BusinessObservation ---
            key_values = self._extract_key_values(text, summary_hints)
            observations.append(BusinessObservation(
                domain=domain,
                report_type=report_type,
                source_file=source_file,
                sheet=sheet,
                key_values=key_values,
                raw_text=display_text,
                relevance_score=score,
            ))

        formatted = "\n".join(lines)
        return DomainSection(
            domain=domain,
            document_count=len(nodes),
            formatted_text=formatted,
            observations=observations,
        )

    @staticmethod
    def _extract_key_values(text: str, summary_hints: list[str]) -> dict[str, str]:
        """
        Parse key: value pairs from a node's text for structured observation.

        Prefers summary_hint keys (domain-specific); falls back to all KV pairs.
        """
        kv_pairs = {
            k.strip().lower(): v.strip()
            for k, v in _KV_RE.findall(text)
            if v.strip()
        }

        if not summary_hints:
            return dict(list(kv_pairs.items())[:10])

        # Filter to domain-relevant keys first
        selected: dict[str, str] = {}
        for hint in summary_hints:
            for key, val in kv_pairs.items():
                if hint.lower() in key:
                    selected[key] = val
                    break

        # Supplement with remaining pairs up to limit
        for key, val in kv_pairs.items():
            if key not in selected and len(selected) < 10:
                selected[key] = val

        return selected

    def _assemble_context(
        self, sections: list[DomainSection], plan: RetrievalPlan
    ) -> str:
        """
        Produce the final structured context string for the LLM prompt.
        Includes domain summaries derived from observations.
        """
        header_label = _QUERY_TYPE_HEADERS.get(
            plan.query_type, "BUSINESS DATA CONTEXT"
        )
        intent_instruction = _INTENT_INSTRUCTIONS.get(
            plan.intent, "Answer the question using the data below."
        )

        lines: list[str] = [
            f"=== {header_label} ===",
            f"Instruction: {intent_instruction}",
        ]

        # Time range banner
        if plan.time_range and plan.time_range.label:
            lines.append(f"Time Period: {plan.time_range.label}")

        lines.append("")

        for section in sections:
            domain_label = _DOMAIN_LABELS.get(section.domain, section.domain.value.title())
            lines.append(f"--- {domain_label} ({section.document_count} record(s)) ---")

            # Structured summary from observations
            summary = self._build_domain_summary(section)
            if summary:
                lines.append(summary)

            lines.append(section.formatted_text)
            lines.append("")

        lines.append("=== END OF CONTEXT ===")
        return "\n".join(lines)

    @staticmethod
    def _build_domain_summary(section: DomainSection) -> str:
        """
        Produce a terse domain summary from the section's key_values.
        This gives the LLM a quick-reference header before the raw records.
        """
        if not section.observations:
            return ""

        # Aggregate unique values per key across all observations
        agg: dict[str, list[str]] = defaultdict(list)
        for obs in section.observations:
            for k, v in obs.key_values.items():
                if v not in agg[k]:
                    agg[k].append(v)

        if not agg:
            return ""

        summary_lines = [f"  Summary:"]
        for key, values in list(agg.items())[:5]:
            vals_str = ", ".join(values[:3])
            summary_lines.append(f"    {key.title()}: {vals_str}")

        return "\n".join(summary_lines)
