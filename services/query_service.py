"""
services/query_service.py

Top-level orchestrator for the Business Query Intelligence + Reasoning pipeline.

Full pipeline sequence:
  1. IntentService.analyze(question)               →  RetrievalPlan
  2. RetrievalService.retrieve(question, plan)      →  list[NodeWithScore]
  3. BusinessContextBuilder.build(nodes, plan)      →  BusinessContext
  4. BusinessReasoningService.reason(context)       →  ReasoningContext
  5. RagService.generate_response(q, reasoning_ctx) →  LlamaIndex Response

Design rules:
  - No business logic here.
  - No LLM calls here (RagService owns that).
  - No document parsing here (IngestionService owns that).
  - No reasoning logic here (BusinessReasoningService owns that).
  - QueryService is a pure coordinator of injected collaborators.
  - Every collaborator is injected or constructed predictably.
"""

import time

from core.logging import get_logger
from services.intent_service import BaseIntentAnalyzer, RuleBasedIntentAnalyzer
from services.retrieval_service import RetrievalService
from services.context_builder import BusinessContextBuilder
from services.business_reasoning_service import BusinessReasoningService
from services.analytics_service import AnalyticsService
from services.forecasting_service import ForecastingService
from services.rag_service import RagService
from schemas.query_context import BusinessContext
from schemas.reasoning_context import ReasoningContext
from schemas.retrieval_plan import RetrievalPlan

logger = get_logger(__name__)


class QueryService:
    """
    Orchestrates the full Business Query Intelligence + Reasoning pipeline.

    Args:
        rag_service:       Singleton RagService from application state.
        intent_analyzer:   Defaults to RuleBasedIntentAnalyzer; inject
                           LLMIntentAnalyzer when available.
    """

    def __init__(
        self,
        rag_service: RagService,
        intent_analyzer: BaseIntentAnalyzer | None = None,
    ) -> None:
        self._rag_service = rag_service
        self._intent_analyzer: BaseIntentAnalyzer = (
            intent_analyzer or RuleBasedIntentAnalyzer()
        )
        self._retrieval_service = RetrievalService(index=rag_service.index)
        self._context_builder = BusinessContextBuilder()
        self._reasoning_service = BusinessReasoningService()
        self._analytics_service = AnalyticsService()
        self._forecasting_service = ForecastingService()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def answer(self, question: str):
        """
        Execute the full query + reasoning pipeline and return a
        LlamaIndex Response-compatible object.

        Args:
            question: The user's raw natural language question.

        Returns:
            llama_index Response — compatible with the existing map_response mapper.
        """
        t0 = time.perf_counter()

        # Step 1: Analyze intent
        plan: RetrievalPlan = self._intent_analyzer.analyze(question)
        t1 = time.perf_counter()
        logger.info(
            f"QueryService [intent]: {plan.intent.value}, "
            f"domains={[d.value for d in plan.domains]}, "
            f"confidence={plan.confidence:.3f} "
            f"({(t1 - t0) * 1000:.1f}ms)"
        )

        # Step 2: Retrieve relevant documents
        nodes = self._retrieval_service.retrieve(question, plan)
        t2 = time.perf_counter()
        logger.info(
            f"QueryService [retrieval]: {len(nodes)} node(s) "
            f"({(t2 - t1) * 1000:.1f}ms)"
        )

        # Step 3: Build structured business context with observations
        business_context: BusinessContext = self._context_builder.build(nodes, plan)
        t3 = time.perf_counter()
        logger.info(
            f"QueryService [context]: {business_context.total_documents} doc(s), "
            f"{len(business_context.sections)} domain section(s) "
            f"({(t3 - t2) * 1000:.1f}ms)"
        )

        # Step 4: Cross-domain business reasoning
        reasoning_context: ReasoningContext = self._reasoning_service.reason(business_context)
        t4 = time.perf_counter()
        logger.info(
            f"QueryService [reasoning]: {len(reasoning_context.insights)} insight(s), "
            f"{len(reasoning_context.relationships)} relationship(s), "
            f"confidence={reasoning_context.overall_confidence:.3f} "
            f"({(t4 - t3) * 1000:.1f}ms)"
        )

        # Step 4.5: Deterministic Business Analytics
        # Extract all observations from context sections
        all_observations = []
        for section in business_context.sections:
            all_observations.extend(section.observations)
            
        analytics_context = self._analytics_service.compute(all_observations, plan)
        ta = time.perf_counter()
        logger.info(
            f"QueryService [analytics]: {len(analytics_context.metrics)} metric(s) computed "
            f"({(ta - t4) * 1000:.1f}ms)"
        )

        # Step 5: Deterministic Forecasting (only if plan requests it)
        forecast_context = None
        tf = ta
        if plan.forecast_metrics:
            forecast_context = self._forecasting_service.compute(all_observations, plan)
            tf = time.perf_counter()
            logger.info(
                f"QueryService [forecasting]: {len(forecast_context.results)} result(s) "
                f"({(tf - ta) * 1000:.1f}ms)"
            )

        # Step 6: Generate LLM response with reasoning, analytics, and forecast context
        response = self._rag_service.generate_response(
            question=question,
            reasoning_context=reasoning_context,
            analytics_context=analytics_context,
            forecast_context=forecast_context,
        )
        t5 = time.perf_counter()
        logger.info(
            f"QueryService [generation]: complete "
            f"({(t5 - tf) * 1000:.1f}ms) "
            f"| total pipeline={(t5 - t0) * 1000:.1f}ms"
        )

        return response
