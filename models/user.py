"""
models/user.py

SQLAlchemy 2.0 ORM definition for the User table and the Role enum.

Design decision: SQLite is used as the database for user accounts because
SQLAlchemy is already present in the venv (pulled in by LlamaIndex).
Switching to PostgreSQL later requires only changing the DATABASE_URL
environment variable and installing the psycopg2 driver — nothing else changes.
"""

import os
from enum import Enum as PyEnum
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./users.db")

# ---------------------------------------------------------------------------
# Database engine & session factory
# ---------------------------------------------------------------------------
# connect_args is SQLite-only; remove it when moving to Postgres
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Role enum
# ---------------------------------------------------------------------------
class Role(str, PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


# ---------------------------------------------------------------------------
# User ORM model
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(64), unique=True, index=True, nullable=False)
    email: str = Column(String(256), unique=True, index=True, nullable=False)
    password_hash: str = Column(String(256), nullable=False)
    role: Role = Column(
        Enum(Role, name="role_enum", create_constraint=True),
        nullable=False,
        default=Role.VIEWER,
    )
    is_active: bool = Column(Boolean, default=True, nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def get_db():
    """
    FastAPI dependency that yields a database session and guarantees cleanup.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
