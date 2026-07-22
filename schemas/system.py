from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """Health check response containing critical service status."""
    status: str = Field(..., description="Overall status of the service (e.g., 'ok').")
    uptime_seconds: float = Field(..., description="Total uptime of the FastAPI application in seconds.")
    server_time: str = Field(..., description="Current UTC time on the server.")
    version: str = Field(..., description="Current version of the application.")
    llm_loaded: bool = Field(..., description="Indicates if the Language Model was loaded successfully.")
    embedding_loaded: bool = Field(..., description="Indicates if the Embedding Model was loaded successfully.")
    index_loaded: bool = Field(..., description="Indicates if the VectorStoreIndex is loaded in memory.")

class IndexStatsResponse(BaseModel):
    """Statistics about the underlying document index."""
    indexed_files: int = Field(..., description="Total number of files tracked in metadata.")
    indexed_documents: int = Field(..., description="Total number of chunked documents stored in the index.")
    storage_directory: str = Field(..., description="The path to the persistent storage directory.")
    storage_size_bytes: int = Field(..., description="Total size of the storage directory in bytes.")
    last_indexing_timestamp: float | None = Field(default=None, description="Unix timestamp of the last index modification.")

class ModelConfigsResponse(BaseModel):
    """Information about active ML models in the RAG pipeline."""
    llm_provider: str = Field(..., description="Provider class of the Language Model.")
    llm_model: str = Field(..., description="Name of the active LLM.")
    embedding_model: str = Field(..., description="Name of the active embedding model.")
    vector_store_type: str = Field(..., description="Type of the active vector store.")
