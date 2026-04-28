"""Processed data model for storing structured data from external sources."""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func

from app.core.database import Base


class ProcessedData(Base):
    """Store processed data from external sources."""

    __tablename__ = "processed_data"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), nullable=False, index=True)  # economy, health, education, environment, demography, meteo, agriculture
    indicator = Column(String(255), nullable=False, index=True)
    region = Column(String(100), nullable=True, index=True)  # For regional data
    date_value = Column(DateTime(timezone=True), nullable=False, index=True)
    numeric_value = Column(Float, nullable=True)
    text_value = Column(Text, nullable=True)
    metadata = Column(JSON, default={})  # Additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProcessedData {self.domain}/{self.indicator}>"
