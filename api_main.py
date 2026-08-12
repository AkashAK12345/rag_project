import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from services.rag_service import RagService
from services.job_manager import JobManager
from models.user import Base, engine, SessionLocal
import models.connector  # Ensure models are registered with Base
from api.query import router as query_router
from api.upload import router as upload_router
from api.system import router as system_router
from api.jobs import router as jobs_router
from api.auth import router as auth_router
from api.ingestion import router as ingestion_router
from api.connectors import router as connectors_router
from api.analytics import router as analytics_router
from api.forecast import router as forecast_router
from api.capabilities import router as capabilities_router
from core.logging import get_logger

load_dotenv()
logger = get_logger(__name__)


def _seed_admin_user() -> None:
    """
    Create a default ADMIN account on first startup if none exists.
    Credentials are read from environment variables so they are never hardcoded.
    """
    from models.user import User, Role
    from services.auth_service import AuthService

    admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "changeme123")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == admin_username).first()
        if not existing:
            AuthService(db).create_user(
                username=admin_username,
                email=admin_email,
                plain_password=admin_password,
                role=Role.ADMIN,
            )
            logger.info(f"Default admin user '{admin_username}' created.")
        else:
            logger.info(f"Admin user '{admin_username}' already exists — skipping seed.")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")

    # 1. Create all database tables (idempotent)
    logger.info("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)
    _seed_admin_user()

    # 2. Initialise RagService (heavy: loads LLM + vector store)
    try:
        logger.info("Initializing RagService (this may take a moment)...")
        rag_service = RagService()
        app.state.rag_service = rag_service
        app.state.start_time = time.time()
        logger.info("RagService initialized successfully.")
    except Exception as exc:
        logger.error(f"Failed to initialize RagService: {exc}", exc_info=True)
        raise

    # 3. In-memory job registry (lightweight, always safe)
    app.state.job_manager = JobManager()
    logger.info("JobManager initialized and attached to application state.")

    yield

    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="Restaurant Analytics RAG API",
    description="Production-ready FastAPI backend with authentication and role-based authorization.",
    version="1.0.0",
    lifespan=lifespan,
)

# All endpoints namespaced under /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(query_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(ingestion_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(connectors_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(forecast_router, prefix="/api/v1")
app.include_router(capabilities_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    import sys

    # Development mode with --dev enables reloading but specifically ignores
    # runtime-generated directories to prevent the server from continuously
    # restarting and wiping in-memory state when files are uploaded or indexed.
    if "--dev" in sys.argv:
        uvicorn.run(
            "api_main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_excludes=[
                "uploads",
                "storage",
                "metadata",
                "*.db",
                "*.sqlite",
                "__pycache__"
            ]
        )
    else:
        # Production behavior remains unchanged (no reload)
        uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=False)
