"""
Reminder Job model for scheduling and tracking reminder notifications.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum as SAEnum

from app.core.database import Base, GUID
import enum


class ReminderType(str, enum.Enum):
    """Types of reminders."""
    MEDICAL_VISIT = "MEDICAL_VISIT"
    LEGAL_DOCUMENT = "LEGAL_DOCUMENT"
    INSPECTION = "INSPECTION"
    FOLLOW_UP = "FOLLOW_UP"
    GENERAL = "GENERAL"


class ReminderStatus(str, enum.Enum):
    """Reminder job status."""
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReminderJob(Base):
    """Reminder job database model."""

    __tablename__ = "reminder_jobs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(GUID(), nullable=False, index=True)
    reminder_type = Column(
        SAEnum(ReminderType, name="reminder_type_enum"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    delivery_channel = Column(String(50), default="WHATSAPP")
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(
        SAEnum(ReminderStatus, name="reminder_status_enum"),
        default=ReminderStatus.SCHEDULED,
        nullable=False,
    )
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
