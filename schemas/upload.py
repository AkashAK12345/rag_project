from pydantic import BaseModel, Field

class UploadResponse(BaseModel):
    """Response model for the /upload endpoint."""
    uploaded_files: list[str] = Field(default_factory=list, description="List of successfully uploaded and processed files.")
    skipped_files: list[str] = Field(default_factory=list, description="List of files that were skipped (e.g. already indexed).")
    indexed_documents: int = Field(0, description="Total number of documents generated and indexed from the uploaded files.")
    processing_time_ms: float = Field(..., description="Time taken to upload and index the files in milliseconds.")
    message: str = Field(..., description="A summary message of the upload and indexing process.")
