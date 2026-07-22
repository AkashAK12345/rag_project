from pydantic import BaseModel, Field, EmailStr
from models.user import Role


class LoginRequest(BaseModel):
    """Request body for POST /api/v1/auth/login."""
    username: str = Field(..., description="Username of the account.")
    password: str = Field(..., description="Plain-text password (transmitted over TLS only).")


class TokenResponse(BaseModel):
    """Successful login response containing the JWT access token."""
    access_token: str = Field(..., description="Signed JWT access token.")
    token_type: str = Field(default="bearer", description="Always 'bearer'.")
    expires_in: int = Field(..., description="Token lifetime in seconds.")


class UserResponse(BaseModel):
    """Safe, serializable view of the authenticated user (never exposes password_hash)."""
    id: int
    username: str
    email: str
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}


class LogoutResponse(BaseModel):
    """Stateless logout confirmation."""
    message: str = Field(default="Logged out successfully.")
