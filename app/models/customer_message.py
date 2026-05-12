"""
Customer Message model for tracking all outgoing communications.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Index

from app.core.database import Base, GUID
import enum


class MessageType(str, enum.Enum):
    """Types of messages."""
    REMINDER = "REMINDER"
    ALERT = "ALERT"
    NOTIFICATION = "NOTIFICATION"
    CONFIRMATION = "CONFIRMATION"
    PROMOTIONAL = "PROMOTIONAL"


class DeliveryChannel(str, enum.Enum):
    """Communication delivery channels."""
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"


class MessageStatus(str, enum.Enum):
    """Message delivery status."""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRY = "RETRY"


class CustomerMessage(Base):
    """Customer message database model."""

    __tablename__ = "customer_messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(GUID(), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    mobile_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    message_type = Column(SAEnum(MessageType, name="message_type_enum"), nullable=False)
    delivery_channel = Column(SAEnum(DeliveryChannel, name="delivery_channel_enum"), nullable=False)
    status = Column(
        SAEnum(MessageStatus, name="message_status_enum"),
        default=MessageStatus.PENDING,
        nullable=False,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_customer_messages_status_channel", "status", "delivery_channel"),
    )
