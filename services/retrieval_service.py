"""
services/retrieval_service.py

Metadata-aware document retrieval. The only layer that directly interacts
with the LlamaIndex vector store retriever.

Responsibilities:
  - Accept a RetrievalPlan.
  - Build MetadataFilters from the plan's domains and report_types.
  - Query the vector store retriever (no LLM call — embedding only).
  - Return a ranked list of NodeWithScore objects for ContextBuilder.

Design rules:
  - Never calls the LLM.
  - Never constructs prompts.
  - Never contains business logic.
  - Falls back gracefully if the index has no metadata filters configured.
"""

from core.logging import get_logger
from schemas.retrieval_plan import RetrievalPlan
from schemas.report import BusinessDomain

logger = get_logger(__name__)


class RetrievalService:
    """
    Executes a RetrievalPlan against the vector store.

    The index is injected (not constructed here) so that the singleton
    loaded at startup in RagService is reused — models and embeddings
    are never reloaded.
    """

    def __init__(self, index) -> None:
        """
        Args:
            index: LlamaIndex VectorStoreIndex instance from RagService.
        """
        self._index = index

    def retrieve(self, question: str, plan: RetrievalPlan) -> list:
        """
        Retrieve the top-k most relevant document nodes for the given
        question, constrained by the domains and report_types in the plan.

        Args:
            question: The original user query string.
            plan:     The RetrievalPlan from IntentService.

        Returns:
            A list of llama_index NodeWithScore objects, ranked by similarity.
        """
        logger.info(
            f"RetrievalService: retrieving top_k={plan.top_k} for "
            f"domains={[d.value for d in plan.domains]}"
            + (f", time_range={plan.time_range.label}" if plan.time_range else "")
        )

        # Build metadata filters from the plan
        filters = self._build_filters(plan)

        # Create a retriever with the configured top_k and optional filters
        retriever_kwargs: dict = {"similarity_top_k": plan.top_k}
        if filters is not None:
            retriever_kwargs["filters"] = filters

        retriever = self._index.as_retriever(**retriever_kwargs)
        nodes = retriever.retrieve(question)

        logger.info(f"RetrievalService: retrieved {len(nodes)} node(s)")
        return nodes

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_filters(self, plan: RetrievalPlan):
        """
        Construct LlamaIndex MetadataFilters from the plan's domains and time_range.

        Returns None if:
          - domains is empty or contains only UNKNOWN (no filtering needed)
          - MetadataFilters is not available in this LlamaIndex version

        Falls back gracefully so the system still works even if metadata
        was not written during ingestion (e.g., files indexed by the
        legacy ExcelLoader before the ingestion framework was introduced).
        """
        from llama_index.core.vector_stores import (
            MetadataFilter,
            MetadataFilters,
            FilterOperator,
            FilterCondition,
        )

        all_filter_groups: list = []

        # --- Domain filters ---
        meaningful_domains = [
            d for d in plan.domains if d != BusinessDomain.UNKNOWN
        ]

        if meaningful_domains:
            domain_filters = [
                MetadataFilter(
                    key="business_domain",
                    value=domain.value,
                    operator=FilterOperator.EQ,
                )
                for domain in meaningful_domains
            ]
            if len(domain_filters) == 1:
                all_filter_groups.extend(domain_filters)
            else:
                # Wrap multi-domain in OR sub-group
                all_filter_groups.append(
                    MetadataFilters(
                        filters=domain_filters,
                        condition=FilterCondition.OR,
                    )
                )
        else:
            logger.debug("RetrievalService: no domain filter applied (UNKNOWN domain).")

        # --- Time range filter ---
        # Uses the reporting_period metadata field stored during ingestion.
        # Applies a simple CONTAINS match on the label (e.g., "July 2025").
        # Falls back gracefully if reporting_period was not indexed.
        if plan.time_range and plan.time_range.label:
            time_filter = MetadataFilter(
                key="reporting_period",
                value=plan.time_range.label,
                operator=FilterOperator.CONTAINS
                if hasattr(FilterOperator, "CONTAINS")
                else FilterOperator.EQ,
            )
            all_filter_groups.append(time_filter)
            logger.info(
                f"RetrievalService: time_range filter applied: '{plan.time_range.label}'"
            )

        if not all_filter_groups:
            return None

        if len(all_filter_groups) == 1:
            # Single filter — unwrap if it's already a MetadataFilters sub-group
            if isinstance(all_filter_groups[0], MetadataFilters):
                return all_filter_groups[0]
            return MetadataFilters(filters=all_filter_groups)

        # Multiple filter groups — join with AND (domain OR + time filter)
        return MetadataFilters(
            filters=all_filter_groups,
            condition=FilterCondition.AND,
        )
