"""Dataset model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Dataset(Base):
    """Dataset model for storing dataset metadata."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    domain = Column(String(50), nullable=True, index=True)
    source_type = Column(String(100), nullable=True)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    columns_info = Column(JSON, default=[])  # Array of column metadata
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", lazy="select")
    ml_models = relationship("MLModel", back_populates="dataset", lazy="select")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, rows={self.row_count})>"
