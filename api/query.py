import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from schemas.query import QueryRequest, QueryResponse
from api.dependencies import get_query_service, require_roles, get_rag_service
from api.mappers import map_response
from models.user import Role
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.ANALYST))]
)
def query_rag(
    request: QueryRequest,
    query_service=Depends(get_query_service),
):
    """
    Execute a business intelligence query against the RAG pipeline.
    """
    logger.info(f"Received query: '{request.question}'")
    try:
        start_time = time.perf_counter()
        response = query_service.answer(request.question)
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Query pipeline completed in {latency_ms:.2f}ms")
        return map_response(response=response, latency_ms=latency_ms)
    except Exception as e:
        logger.error(f"Error during query execution: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your query.",
        )
