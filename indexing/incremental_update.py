import config.settings
from services.indexing_service import IndexingService
from core.logging import get_logger

logger = get_logger(__name__)

def run_incremental_update():
    """
    CLI entry point for incremental indexing.
    Delegates business logic to the IndexingService.
    """
    logger.info("CLI: Triggering incremental update via IndexingService")
    service = IndexingService()
    stats = service.run_incremental_update()
    logger.info(f"CLI: Incremental update complete. Stats: {stats}")

if __name__ == "__main__":
    run_incremental_update()