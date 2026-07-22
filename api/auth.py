from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.logging import get_logger
from models.user import User, get_db
from schemas.auth import LoginRequest, TokenResponse, UserResponse, LogoutResponse
from services.auth_service import AuthService
from api.dependencies import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain a JWT access token",
    description="Authenticates with username and password and returns a signed JWT.",
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # NEVER log the password
    logger.info(f"Login attempt for username='{request.username}'")
    try:
        token_response = AuthService(db).authenticate(
            username=request.username,
            plain_password=request.password,
        )
        return token_response
    except ValueError as exc:
        # ValueError from AuthService = bad credentials (intentionally vague to client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as exc:
        logger.error(f"Unexpected error during login: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during authentication.",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    description="Returns the profile of the user associated with the supplied JWT.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout (stateless)",
    description=(
        "Stateless JWT logout — the token remains technically valid until it expires. "
        "Clients should discard the token immediately on receipt of this response."
    ),
)
async def logout(current_user: User = Depends(get_current_user)):
    logger.info(f"User '{current_user.username}' logged out.")
    return LogoutResponse(message="Logged out successfully.")
