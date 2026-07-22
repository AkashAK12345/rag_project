from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for the /query endpoint."""
    question: str = Field(..., description="The question to ask the RAG system.", example="What is the company's leave policy?")


class SourceDocument(BaseModel):
    """Structured representation of a retrieved document node preview."""
    file: str = Field(..., description="The origin filename of the document.")
    sheet: str | None = Field(default=None, description="The sheet name if applicable.")
    score: float = Field(..., description="The similarity or relevance score.")
    preview: str = Field(..., description="A short preview of the retrieved text.")


class ResponseMetadata(BaseModel):
    """Metadata regarding the query execution."""
    latency_ms: float = Field(..., description="Time taken to generate the response in milliseconds.")
    model: str = Field(..., description="The LLM model used for generation.")
    retrieved_documents: int = Field(..., description="Number of source documents retrieved.")


class QueryResponse(BaseModel):
    """Response model for the /query endpoint."""
    answer: str = Field(..., description="The generated answer from the LLM.")
    sources: list[SourceDocument] = Field(default_factory=list, description="List of source document previews used to generate the answer.")
    metadata: ResponseMetadata | None = Field(default=None, description="Optional metadata about the query execution.")
