"""
Communication Log model for tracking all communication activity.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, Index

from app.core.database import Base, GUID
import enum


class LogEventType(str, enum.Enum):
    """Types of log events."""
    SEND = "SEND"
    DELIVERY = "DELIVERY"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    BOUNCE = "BOUNCE"
    ESCALATION = "ESCALATION"


class LogChannel(str, enum.Enum):
    """Communication channels."""
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"
    MULTI = "MULTI"


class LogStatus(str, enum.Enum):
    """Log entry status."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    RETRYING = "RETRYING"


class CommunicationLog(Base):
    """Communication log database model."""

    __tablename__ = "communication_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_type = Column(SAEnum(LogEventType, name="log_event_type_enum"), nullable=False)
    channel = Column(SAEnum(LogChannel, name="log_channel_enum"), nullable=False)
    recipient = Column(String(255), nullable=False, index=True)
    notification_id = Column(GUID(), nullable=True)
    status = Column(SAEnum(LogStatus, name="log_status_enum"), nullable=False)
    response_message = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    __table_args__ = (
        Index("ix_comm_logs_event_channel", "event_type", "channel"),
    )
