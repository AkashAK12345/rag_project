import pytest

@pytest.mark.integration
def test_rag_query():
    try:
        from tools.rag_tool import RAGTool
        tool = RAGTool()
        response = tool.run(
            "What information is available in the purchase report?"
        )
    except Exception as e:
        error_msg = str(e).lower()
        type_name = type(e).__name__.lower()
        # Skip only for specific Ollama environment issues
        if "out of memory" in error_msg or "connection" in error_msg or "connecterror" in type_name or "timeout" in type_name or "responseerror" in type_name:
            pytest.skip(f"Ollama service unavailable or OOM: {e}")
        raise # Genuine failure
        
    assert isinstance(response, str)
    assert len(response.strip()) > 0