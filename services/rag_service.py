# services/rag_service.py

import os
import threading

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
        self._lock = threading.Lock()

        self._configure_models()

        # Expose the index so RetrievalService can create targeted retrievers
        self.index = self._load_index()

        # Default query engine (used by legacy .query() path if needed)
        self.query_engine = self.index.as_query_engine(
            streaming=False,
            similarity_top_k=3,
        )

    def reload_index(self) -> None:
        """
        Reload the vector index from disk into memory.
        Used to refresh the singleton state after new documents are ingested.
        """
        logger.info("RagService.reload_index: Loading updated index from storage...")
        new_index = self._load_index()
        new_query_engine = new_index.as_query_engine(
            streaming=False,
            similarity_top_k=3,
        )
        
        with self._lock:
            self.index = new_index
            self.query_engine = new_query_engine
            
        logger.info("RagService.reload_index: Index successfully refreshed in memory.")

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
        capability_context=None,
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
            
        if capability_context is not None:
            cap_lines = [
                "--- CAPABILITY CONTEXT ---",
                f"Supported Domains: {', '.join(capability_context.supported_domains)}",
                f"Unsupported Domains: {', '.join(capability_context.unsupported_domains)}",
                f"Supported Metrics: {', '.join(capability_context.supported_metrics)}",
                f"Supported Charts: {', '.join(capability_context.supported_charts)}",
                "If the question asks about unsupported domains, state clearly that the data is not available.",
                "--------------------------"
            ]
            prompt_body += "\n\n" + "\n".join(cap_lines)

        # --- Build a grounding block from source context ---
        # This is injected at the TOP of the prompt so the LLM cannot
        # invent sources or confuse retrieved document count with record count.
        grounding_lines = []
        if reasoning_context is not None and hasattr(reasoning_context, "source_context"):
            source_ctx = reasoning_context.source_context
            total_docs = getattr(source_ctx, "total_documents", 0)
            sections = getattr(source_ctx, "sections", [])
            source_files = sorted({
                obs.source_file
                for section in sections
                for obs in section.observations
                if obs.source_file
            })
            grounding_lines.append(
                f"Evidence: {total_docs} retrieved document(s) from the vector store."
            )
            if source_files:
                grounding_lines.append(
                    f"Source file(s): {', '.join(source_files)}"
                )
                logger.info(f"RagService: using metadata — files={source_files}")
        grounding_note = (
            "=== GROUNDING CONSTRAINTS ===\n"
            + "\n".join(grounding_lines)
            + "\n=== END GROUNDING ==="
        ) if grounding_lines else ""

        # --- Assemble the full prompt ---
        system_instructions = (
            "You are a precise, evidence-based business analyst assistant.\n"
            "STRICT RULES — follow these before generating any word of your response:\n"
            "  1. Use ONLY the information explicitly present in the retrieved context below.\n"
            "  2. Do NOT invent observations, metrics, KPIs, recommendations, or insights\n"
            "     that are not directly supported by the retrieved data.\n"
            "  3. Do NOT infer totals, averages, or trends unless they are explicitly\n"
            "     stated in the retrieved context.\n"
            "  4. Do NOT confuse the number of retrieved_documents with the number of\n"
            "     business records (e.g., employee count, transaction count).\n"
            "  5. If the retrieved evidence is insufficient to answer the question,\n"
            "     explicitly state what information IS available and what is MISSING.\n"
            "  6. Distinguish clearly between: (a) facts from the data, (b) inferences\n"
            "     you are drawing, and (c) information that is unavailable.\n"
            "  7. Avoid generic executive language. Be concise and grounded.\n"
        )

        if analytics_context is not None and analytics_context.analytics_text:
            system_instructions += (
                "  8. The Deterministic Analytics section contains pre-computed facts.\n"
                "     Do NOT recalculate those metrics. Use them as ground truth to\n"
                "     explain what happened and reference the Cross-Domain Insights\n"
                "     to explain why.\n"
            )

        if forecast_context is not None and forecast_context.results:
            system_instructions += (
                "  9. The Forecasting Results section contains pre-computed predictions.\n"
                "     Do NOT recalculate or re-derive them. Explain what the forecast\n"
                "     means for the business, reference the methodology and confidence,\n"
                "     and highlight the prediction interval.\n"
            )

        prompt_parts = []
        if grounding_note:
            prompt_parts.append(grounding_note)
        prompt_parts.append(prompt_body)
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append(system_instructions)

        prompt = "\n\n".join(prompt_parts)

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