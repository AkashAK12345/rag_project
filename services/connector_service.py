"""
services/connector_service.py

Manages lifecycle and persistence of Connector configurations in the database.
"""

from typing import List
from sqlalchemy.orm import Session
import uuid

from models.connector import ConnectorModel
from schemas.connector_config import ConnectorCreate


class ConnectorService:
    def __init__(self, db: Session):
        self.db = db

    def create_connector(self, data: ConnectorCreate) -> ConnectorModel:
        connector_id = str(uuid.uuid4())
        
        db_connector = ConnectorModel(
            id=connector_id,
            name=data.name,
            source_type=data.source_type,
            organization_id=data.organization_id,
            config=data.config
        )
        
        self.db.add(db_connector)
        self.db.commit()
        self.db.refresh(db_connector)
        
        return db_connector

    def get_connector(self, connector_id: str) -> ConnectorModel | None:
        return self.db.query(ConnectorModel).filter(ConnectorModel.id == connector_id).first()

    def list_connectors(self, organization_id: str | None = None) -> List[ConnectorModel]:
        query = self.db.query(ConnectorModel)
        if organization_id:
            query = query.filter(ConnectorModel.organization_id == organization_id)
        return query.all()

    def delete_connector(self, connector_id: str) -> bool:
        db_connector = self.get_connector(connector_id)
        if not db_connector:
            return False
            
        self.db.delete(db_connector)
        self.db.commit()
        return True
