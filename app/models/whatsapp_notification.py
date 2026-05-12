"""
WhatsApp Notification model for tracking WhatsApp message delivery.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum as SAEnum

from app.core.database import Base, GUID
import enum


class WhatsAppStatus(str, enum.Enum):
    """WhatsApp delivery status."""
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"


class WhatsAppNotification(Base):
    """WhatsApp notification database model."""

    __tablename__ = "whatsapp_notifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    recipient_phone = Column(String(20), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=True)
    template_id = Column(GUID(), nullable=True)
    message_body = Column(Text, nullable=False)
    status = Column(
        SAEnum(WhatsAppStatus, name="whatsapp_status_enum"),
        default=WhatsAppStatus.QUEUED,
        nullable=False,
    )
    provider_message_id = Column(String(255), nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
