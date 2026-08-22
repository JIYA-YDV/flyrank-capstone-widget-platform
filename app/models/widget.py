# app/models/widget.py
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    widget_type = Column(String(50), nullable=False)  # "signup_form", "contact_form", "cta_popover"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    fields_config = Column(JSONB, nullable=False, default=list)
    button_text = Column(String(100), nullable=False, default="Submit")
    display_options = Column(JSONB, nullable=True, default=dict)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(String(10), nullable=False, default="active")  # "active" / "inactive"
    allowed_origins = Column(JSONB, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="widgets")
    submissions = relationship("Submission", back_populates="widget", cascade="all, delete-orphan")