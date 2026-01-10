from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid

class SyncConfig(Base):
    __tablename__ = "sync_configs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sheet_id = Column(String(255), nullable=False)
    sheet_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    column_mapping = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())