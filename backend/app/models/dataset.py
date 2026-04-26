"""Dataset model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dataset(Base):
    """Dataset model for storing dataset metadata."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    source = Column(String(100), nullable=False)
    domain = Column(String(50), nullable=False, index=True)
    row_count = Column(Integer, default=0)
    columns = Column(JSONB, default=list)
    schema = Column(JSONB, default=dict)
    meta_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ml_models = relationship("MLModel", back_populates="dataset")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, domain={self.domain})>"
