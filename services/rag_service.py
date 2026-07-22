# services/rag_service.py

import os

from llama_index.core import (
    VectorStoreIndex,
    Settings,
    StorageContext,
    load_index_from_storage,
)

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from loaders.excel_loader import load_excel_documents
from core.logging import get_logger

logger = get_logger(__name__)


class RagService:

    def __init__(self):

        self.persist_dir = "./storage"
        self.data_dir = "./data"

        self._configure_models()

        # Expose the index so RetrievalService can create targeted retrievers
        self.index = self._load_index()

        # Default query engine (used by legacy .query() path if needed)
        self.query_engine = self.index.as_query_engine(
            streaming=False,
            similarity_top_k=3,
        )

    def _configure_models(self):

        Settings.llm = Ollama(
            model="llama3.2:3b",
            request_timeout=600.0,
            context_window=2048,
        )

        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

    def _load_index(self):

        if not os.path.exists(self.persist_dir):

            logger.info("RagService: no existing index found, creating new index...")

            docs = load_excel_documents(self.data_dir)

            index = VectorStoreIndex.from_documents(docs)

            index.storage_context.persist(
                persist_dir=self.persist_dir
            )

            return index

        logger.info("RagService: loading existing index from storage...")

        storage = StorageContext.from_defaults(
            persist_dir=self.persist_dir
        )

        return load_index_from_storage(storage)

    def query(self, question: str):
        """
        Legacy direct query method — uses the default query engine with no
        metadata filtering or context structuring.
        Preserved for backward compatibility during the migration period.
        """
        response = self.query_engine.query(question)
        return response

    def generate_response(
        self,
        question: str,
        context_text: str = "",
        reasoning_context=None,
        analytics_context=None,
        forecast_context=None,
    ):
        """
        Generate an LLM response given a pre-assembled structured context.

        Args:
            question:          The user's raw question.
            context_text:      Pre-assembled context string from BusinessContextBuilder.
            reasoning_context: Optional ReasoningContext from BusinessReasoningService.
                               When provided, uses reasoning_text (which already embeds
                               context_text) for a richer, cross-domain-aware prompt.
            analytics_context: Optional AnalyticsContext from AnalyticsService.
            forecast_context:  Optional ForecastContext from ForecastingService.
                               When provided, a structured FORECASTING RESULTS block
                               is appended to the prompt for LLM explanation.

        Returns a LlamaIndex Response-compatible object so that the existing
        map_response mapper in api/mappers.py continues to work unchanged.
        """
        # Return a custom wrapper that satisfies the map_response mapper interface.

        # Prefer the reasoning-enriched text when available
        if reasoning_context is not None and reasoning_context.reasoning_text:
            prompt_body = reasoning_context.reasoning_text
        else:
            prompt_body = context_text

        if analytics_context is not None and analytics_context.analytics_text:
            prompt_body += "\n\n" + analytics_context.analytics_text

        if forecast_context is not None and forecast_context.results:
            prompt_body += "\n\n" + self._format_forecast_block(forecast_context)

        prompt = (
            f"{prompt_body}\n\n"
            f"Question: {question}\n\n"
            "Instructions: You are GROVIT AI, the Digital CEO of this business.\n"
            "Using only the business data provided above, answer the question accurately and concisely.\n"
            "If the Deterministic Analytics section is present, DO NOT attempt to recalculate "
            "metrics manually. Treat the Analytics section as ground-truth facts. Use it to "
            "explain 'what' happened or 'how much', and use the Cross-Domain Insights to explain 'why'.\n"
            "If the Forecasting Results section is present, DO NOT attempt to recalculate or "
            "re-derive the forecasted values. Treat them as deterministic predictions produced "
            "by a statistical engine. Explain what the forecast means for the business, "
            "reference the methodology and confidence when relevant, and highlight the "
            "prediction interval to set appropriate expectations.\n"
            "If the data does not contain enough information to answer confidently, "
            "state what is available and what is missing. Do not hallucinate."
        )

        logger.info("RagService.generate_response: sending context to LLM.")

        llm_response = Settings.llm.complete(prompt)
        answer_text = str(llm_response)

        class _ContextResponse:
            """
            Minimal wrapper that satisfies the map_response mapper interface.
            source_nodes is empty because documents were retrieved directly via
            RetrievalService; QueryService callers that need source nodes should
            pass them separately.
            """
            def __init__(self, text: str):
                self.response = text
                self.source_nodes = []

            def __str__(self):
                return self.response

        return _ContextResponse(answer_text)

    @staticmethod
    def _format_forecast_block(forecast_context) -> str:
        """
        Format ForecastContext results into a structured prompt block for the LLM.

        Prompt assembly belongs here in RagService, not in ForecastContext.
        The LLM uses this block to explain the forecasts — never to recalculate.
        """
        lines = [
            "--- DETERMINISTIC FORECASTING RESULTS ---",
            "These forecasts were produced by a statistical engine. Do NOT recalculate them.",
            f"Generated at: {forecast_context.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
        ]

        for result in forecast_context.results:
            lines.append(f"## {result.metric.value.replace('_', ' ').title()} Forecast")
            lines.append(f"- Period:       {result.forecast_period}")
            lines.append(f"- Predicted:    {result.predicted_value:,.2f}")
            lines.append(f"- Range:        {result.lower_bound:,.2f} – {result.upper_bound:,.2f}")
            lines.append(f"- Confidence:   {result.confidence * 100:.1f}%")
            lines.append(f"- Algorithm:    {result.algorithm.value} ({result.methodology})")
            lines.append(f"- Data Points:  {result.observations_used} ({result.historical_period})")
            lines.append("")

        if forecast_context.warnings:
            lines.append("## Forecasting Warnings")
            for w in forecast_context.warnings:
                lines.append(f"- WARNING: {w}")
            lines.append("")

        return "\n".join(lines)