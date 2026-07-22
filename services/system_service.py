import os
import time
import json
from datetime import datetime, timezone
from core.logging import get_logger
from services.rag_service import RagService
from llama_index.core import Settings
from schemas.system import HealthResponse, IndexStatsResponse, ModelConfigsResponse

logger = get_logger(__name__)

class SystemService:
    """Encapsulates business logic for application health and monitoring metrics."""

    METADATA_FILE = "./metadata/indexed_files.json"

    def __init__(self, rag_service: RagService, start_time: float):
        self.rag_service = rag_service
        self.start_time = start_time

    def get_health(self) -> HealthResponse:
        """Calculates system health and uptime."""
        uptime = time.time() - self.start_time
        server_time = datetime.now(timezone.utc).isoformat()
        
        # Check if components are loaded in memory
        llm_loaded = Settings.llm is not None
        embedding_loaded = Settings.embed_model is not None
        index_loaded = hasattr(self.rag_service, "index") and self.rag_service.index is not None

        return HealthResponse(
            status="ok",
            uptime_seconds=round(uptime, 2),
            server_time=server_time,
            version="1.0.0",
            llm_loaded=llm_loaded,
            embedding_loaded=embedding_loaded,
            index_loaded=index_loaded
        )

    def get_index_stats(self) -> IndexStatsResponse:
        """Parses vector store and file system to gather index statistics."""
        # 1. Number of indexed files
        indexed_files_count = 0
        last_modified = None
        if os.path.exists(self.METADATA_FILE):
            try:
                with open(self.METADATA_FILE, "r") as f:
                    metadata = json.load(f)
                    indexed_files_count = len(metadata.get("indexed_files", []))
                last_modified = os.path.getmtime(self.METADATA_FILE)
            except Exception as e:
                logger.warning(f"Could not read metadata file: {e}")

        # 2. Number of indexed documents (from memory)
        doc_count = 0
        if hasattr(self.rag_service, "index") and self.rag_service.index:
            docstore = getattr(self.rag_service.index, "docstore", None)
            if docstore and hasattr(docstore, "docs"):
                doc_count = len(docstore.docs)

        # 3. Storage directory size
        storage_dir = self.rag_service.persist_dir
        total_size = 0
        if os.path.exists(storage_dir):
            for dirpath, _, filenames in os.walk(storage_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        
        return IndexStatsResponse(
            indexed_files=indexed_files_count,
            indexed_documents=doc_count,
            storage_directory=storage_dir,
            storage_size_bytes=total_size,
            last_indexing_timestamp=last_modified
        )

    def get_model_configs(self) -> ModelConfigsResponse:
        """Extracts configuration details for active models."""
        # LLM Details
        llm_obj = Settings.llm
        llm_provider = type(llm_obj).__name__ if llm_obj else "unknown"
        llm_model = getattr(llm_obj, "model", "unknown")

        # Embedding Details
        embed_obj = Settings.embed_model
        embedding_model = getattr(embed_obj, "model_name", "unknown")

        # Vector Store Details
        vstore_type = "unknown"
        if hasattr(self.rag_service, "index") and self.rag_service.index:
            vstore = getattr(self.rag_service.index, "vector_store", None)
            vstore_type = type(vstore).__name__ if vstore else "unknown"

        return ModelConfigsResponse(
            llm_provider=llm_provider,
            llm_model=llm_model,
            embedding_model=embedding_model,
            vector_store_type=vstore_type
        )
