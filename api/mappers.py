from llama_index.core.base.response.schema import Response
from llama_index.core import Settings
from schemas.query import QueryResponse, SourceDocument, ResponseMetadata

MAX_PREVIEW_LENGTH = 200

def map_response(response: Response, latency_ms: float) -> QueryResponse:
    """
    Transforms the LlamaIndex Response object into the API QueryResponse DTO.
    Pure Anti-Corruption Layer mapper with no side effects.
    """
    answer_text = str(response)
    
    sources = []
    if hasattr(response, "source_nodes"):
        for source_node in response.source_nodes:
            score = getattr(source_node, "score", 0.0)
            node = getattr(source_node, "node", None)
            
            if node:
                text = getattr(node, "text", "")
                metadata = getattr(node, "metadata", {})
                
                # 'source_file' is the canonical key written by BaseReport._make_document().
                # 'file_name' / 'filename' are legacy fallbacks for older indexed documents.
                file_name = (
                    metadata.get("source_file")
                    or metadata.get("file_name")
                    or metadata.get("filename")
                    or "unknown"
                )
                sheet_name = metadata.get("sheet") or metadata.get("sheet_name") or None
                
                if len(text) > MAX_PREVIEW_LENGTH:
                    preview = text[:MAX_PREVIEW_LENGTH] + "..."
                else:
                    preview = text
                
                sources.append(
                    SourceDocument(
                        file=file_name,
                        sheet=sheet_name,
                        score=score,
                        preview=preview
                    )
                )

    # Retrieve active model from Settings
    active_model = getattr(Settings.llm, "model", "unknown")

    metadata_obj = ResponseMetadata(
        latency_ms=latency_ms,
        model=active_model,
        retrieved_documents=len(sources)
    )

    return QueryResponse(
        answer=answer_text,
        sources=sources,
        metadata=metadata_obj
    )
