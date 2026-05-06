"""Raw data model for storing collected data."""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func

from app.core.database import Base


class RawData(Base):
    """Raw data collected from various sources."""

    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False)
    dataset_name = Column(String(255), nullable=True, index=True)
    data = Column(JSON, nullable=False)
    collected_at = Column(DateTime(timezone=True), nullable=True)
    hash = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    domain = Column(String(100), nullable=True)
    row_data = Column(JSON, nullable=True)
