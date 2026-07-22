"""
core/security.py

Pure cryptographic utilities: password hashing and JWT lifecycle.

Design constraints:
- No I/O, no database access, no HTTP knowledge.
- All configuration is loaded from environment variables via python-dotenv.
- All functions are stateless — safe to call from any thread.
"""

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.logging import get_logger

load_dotenv()

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read once at module import time
# ---------------------------------------------------------------------------
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# ---------------------------------------------------------------------------
# Password hashing context (bcrypt with auto-upgrade)
# ---------------------------------------------------------------------------
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Constant-time comparison of plain text against a stored bcrypt hash.
    Returns True only when they match.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(subject: str, role: str) -> tuple[str, int]:
    """
    Mint a signed JWT.

    Args:
        subject: The username or user ID embedded as the 'sub' claim.
        role:    The user's role embedded as a custom 'role' claim.

    Returns:
        A (token, expires_in_seconds) tuple.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, ACCESS_TOKEN_EXPIRE_MINUTES * 60


def decode_access_token(token: str) -> dict:
    """
    Validate and decode a JWT.

    Returns the decoded payload dict on success.
    Raises jose.JWTError (which callers translate to HTTP 401).
    """
    # JWTError is raised for expired, tampered, or malformed tokens
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
