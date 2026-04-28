"""Plan and Payment models for subscription management."""

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Plan(Base):
    """Subscription plan definition."""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # free, standard, advanced, enterprise
    price_xaf = Column(Integer, nullable=True)  # 0, 1000, 5000, NULL for enterprise
    features = Column(JSON, default={})  # {"max_analyses": 5, "max_datasets": 10, "gemini": true}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan", lazy="select")

    def __repr__(self):
        return f"<Plan {self.name}>"


class Payment(Base):
    """Payment history for subscriptions."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount_xaf = Column(Integer, nullable=False)
    currency = Column(String(3), default="XAF")
    status = Column(String(20), default="pending")  # pending, succeeded, failed, refunded
    payment_provider = Column(String(50), nullable=True)  # mobile_money, stripe, etc
    provider_payment_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"
