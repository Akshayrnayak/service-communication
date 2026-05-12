"""
Alert Event model for emergency and high-priority notifications.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum as SAEnum

from app.core.database import Base, GUID
import enum


class AlertPriority(str, enum.Enum):
    """Alert priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    """Alert processing status."""
    TRIGGERED = "TRIGGERED"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"


class AlertType(str, enum.Enum):
    """Types of alerts."""
    EMERGENCY_HEALTH = "EMERGENCY_HEALTH"
    CRITICAL_INSPECTION = "CRITICAL_INSPECTION"
    LEGAL_DEADLINE = "LEGAL_DEADLINE"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    CUSTOM = "CUSTOM"


class AlertEvent(Base):
    """Alert event database model."""

    __tablename__ = "alert_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    alert_type = Column(SAEnum(AlertType, name="alert_type_enum"), nullable=False, index=True)
    priority = Column(
        SAEnum(AlertPriority, name="alert_priority_enum"),
        default=AlertPriority.HIGH,
        nullable=False,
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    recipient_id = Column(GUID(), nullable=False)
    recipient_phone = Column(String(20), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    channels_used = Column(String(255), default="SMS,WHATSAPP,EMAIL")
    status = Column(
        SAEnum(AlertStatus, name="alert_status_enum"),
        default=AlertStatus.TRIGGERED,
        nullable=False,
    )
    retry_count = Column(Integer, default=0)
    escalation_level = Column(Integer, default=0)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
