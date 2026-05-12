"""
Email Notification model for tracking email delivery.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Enum as SAEnum

from app.core.database import Base, GUID
import enum


class EmailStatus(str, enum.Enum):
    """Email delivery status."""
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    BOUNCED = "BOUNCED"
    FAILED = "FAILED"


class EmailNotification(Base):
    """Email notification database model."""

    __tablename__ = "email_notifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    is_html = Column(Boolean, default=True)
    template_id = Column(GUID(), nullable=True)
    status = Column(
        SAEnum(EmailStatus, name="email_status_enum"),
        default=EmailStatus.QUEUED,
        nullable=False,
    )
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
