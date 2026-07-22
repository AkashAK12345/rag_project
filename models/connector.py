"""
models/connector.py

SQLAlchemy models for persisting Enterprise Connectors and their Sync History.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.user import Base
from schemas.connector_status import ConnectorStatusEnum, SyncStatus


class ConnectorModel(Base):
    """
    Persisted configuration for a data connector.
    """
    __tablename__ = "connectors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # e.g., 'sql', 'rest', 'excel'
    organization_id = Column(String, nullable=True, index=True)
    
    # JSON column for arbitrary config payload (SQLConfig or RESTConfig)
    config = Column(JSON, nullable=False)
    
    status = Column(String, default=ConnectorStatusEnum.ACTIVE.value)
    last_sync_time = Column(DateTime, nullable=True)
    sync_token = Column(String, nullable=True)  # For incremental sync pagination
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sync_history = relationship("SyncHistoryModel", back_populates="connector", cascade="all, delete")


class SyncHistoryModel(Base):
    """
    Record of a synchronization execution for a connector.
    """
    __tablename__ = "sync_history"

    id = Column(String, primary_key=True, index=True)
    connector_id = Column(String, ForeignKey("connectors.id"), index=True)
    sync_type = Column(String, nullable=False)  # MANUAL, INCREMENTAL, FULL
    
    status = Column(String, default=SyncStatus.QUEUED.value)
    
    records_imported = Column(Integer, default=0)
    processing_time_ms = Column(Float, default=0.0)
    
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)

    connector = relationship("ConnectorModel", back_populates="sync_history")
