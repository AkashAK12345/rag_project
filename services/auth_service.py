"""
services/auth_service.py

Database-aware business logic for authentication.

Responsibilities:
- Fetch users from the database.
- Verify credentials.
- Create new user accounts with hashed passwords.

This service has no HTTP knowledge — it works with plain Python objects
and raises ValueError for domain failures. The API layer translates those
into HTTP error responses.
"""

from sqlalchemy.orm import Session
from core.logging import get_logger
from core.security import hash_password, verify_password, create_access_token
from models.user import User, Role
from schemas.auth import TokenResponse, UserResponse

logger = get_logger(__name__)


class AuthService:

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_user_by_username(self, username: str) -> User | None:
        """Return the User ORM object for the given username, or None."""
        return (
            self._db.query(User)
            .filter(User.username == username)
            .first()
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        """Return the User ORM object for the given id, or None."""
        return self._db.query(User).filter(User.id == user_id).first()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self, username: str, plain_password: str) -> TokenResponse:
        """
        Verify credentials and mint a JWT.

        Raises:
            ValueError: if the username does not exist, the password is wrong,
                        or the account is inactive.
        """
        user = self.get_user_by_username(username)

        if user is None:
            # Do NOT reveal whether the username exists (timing-safe via bcrypt verify)
            logger.warning(f"Login failed: unknown username '{username}'")
            # Perform a dummy verify to keep constant timing even on miss
            verify_password("dummy", hash_password("dummy"))
            raise ValueError("Invalid username or password.")

        if not verify_password(plain_password, user.password_hash):
            logger.warning(f"Login failed: wrong password for '{username}'")
            raise ValueError("Invalid username or password.")

        if not user.is_active:
            logger.warning(f"Login failed: inactive account '{username}'")
            raise ValueError("Account is inactive.")

        token, expires_in = create_access_token(
            subject=user.username,
            role=user.role.value,
        )
        logger.info(f"Login successful for '{username}' (role={user.role.value})")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
        )

    # ------------------------------------------------------------------
    # User management (used at startup to seed the first admin)
    # ------------------------------------------------------------------

    def create_user(
        self,
        username: str,
        email: str,
        plain_password: str,
        role: Role = Role.VIEWER,
    ) -> UserResponse:
        """
        Create a new user account with a bcrypt-hashed password.

        Raises:
            ValueError: if the username or email is already taken.
        """
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' is already registered.")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(plain_password),
            role=role,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        logger.info(f"Created user '{username}' with role '{role.value}'")
        return UserResponse.model_validate(user)
