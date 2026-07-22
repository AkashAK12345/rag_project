"""
api/dependencies.py

Centralised FastAPI dependency functions.

Contains:
  - get_rag_service      — retrieves RagService from app.state
  - get_job_manager      — retrieves JobManager from app.state
  - get_query_service    — constructs QueryService with the RagService singleton
  - get_current_user     — decodes JWT and loads the User from the database
  - require_roles(...)   — factory that builds a role-gating dependency
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from core.logging import get_logger
from core.security import decode_access_token
from models.user import User, Role, get_db
from services.rag_service import RagService
from services.job_manager import JobManager

logger = get_logger(__name__)

# OAuth2-style Bearer token extractor — extracts the raw token from the
# Authorization: Bearer <token> header and raises 403 if the header is absent.
_bearer_scheme = HTTPBearer(auto_error=True)


# ---------------------------------------------------------------------------
# Existing dependencies (unchanged behaviour)
# ---------------------------------------------------------------------------

def get_rag_service(request: Request) -> RagService:
    """Retrieve the RagService singleton from application state."""
    rag_service = getattr(request.app.state, "rag_service", None)
    if not rag_service:
        logger.error("Attempted to access RagService, but it is not initialized.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG Service is not initialized.",
        )
    return rag_service


def get_job_manager(request: Request) -> JobManager:
    """Retrieve the JobManager singleton from application state."""
    manager = getattr(request.app.state, "job_manager", None)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job manager is not initialized.",
        )
    return manager


def get_query_service(request: Request):
    """
    Construct a QueryService backed by the RagService singleton.

    QueryService is not a singleton itself because its internal collaborators
    (IntentAnalyzer, RetrievalService, ContextBuilder) are stateless and cheap
    to instantiate per request. The expensive singleton (RagService / index) is
    always reused from app.state.
    """
    from services.query_service import QueryService
    rag_service = get_rag_service(request)
    return QueryService(rag_service=rag_service)


# ---------------------------------------------------------------------------
# Authentication dependency
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT in the Authorization header and return the matching User.

    Raises HTTP 401 for any token problem (missing, expired, tampered).
    Raises HTTP 401 if the user no longer exists or is inactive.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub", "")
        if not username:
            raise JWTError("Missing subject claim.")
    except JWTError as exc:
        logger.warning(f"JWT validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from services.auth_service import AuthService          # local import avoids circular refs
    user = AuthService(db).get_user_by_username(username)
    if user is None or not user.is_active:
        logger.warning(f"Authenticated token refers to missing/inactive user '{username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ---------------------------------------------------------------------------
# Authorization dependency factory
# ---------------------------------------------------------------------------

def require_roles(*allowed_roles: Role):
    """
    Factory that returns a FastAPI dependency enforcing role membership.

    Usage:
        @router.post("/upload", dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))])

    Returns the authenticated User so downstream code can access it if needed.
    Raises HTTP 403 when the user's role is not in allowed_roles.
    """
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                f"Forbidden: user '{current_user.username}' (role={current_user.role.value}) "
                f"attempted to access a resource restricted to {[r.value for r in allowed_roles]}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}.",
            )
        return current_user

    return _check
