# app/models/submission.py
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from sqlalchemy.orm import relationship
from app.db.session import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    widget_id = Column(UUID(as_uuid=True), ForeignKey("widgets.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # denormalized for fast queries
    data = Column(JSONB, nullable=False)
    ip_address = Column(String(45), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    geo_provider = Column(String(50), nullable=True)  # which provider enriched it
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    is_spam = Column(String(10), nullable=False, default="no")  # "yes" / "no"
    email_sent = Column(String(10), nullable=False, default="no")  # "yes" / "no" / "failed"
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    widget = relationship("Widget", back_populates="submissions")