"""Raw data model for storing unprocessed API responses."""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class RawData(Base):
    """Store raw data from external sources."""

    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # world_bank, nasa_power, fao
    dataset_name = Column(String(255), nullable=False, index=True)
    data = Column(JSON, nullable=False)  # Raw API response
    hash = Column(String(64), unique=True, nullable=False, index=True)  # For deduplication
    status = Column(String(20), default="pending")  # pending, processed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<RawData {self.source}/{self.dataset_name}>"
