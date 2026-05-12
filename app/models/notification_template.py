"""
Notification Template model for storing reusable message templates.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, JSON

from app.core.database import Base, GUID
import enum


class TemplateType(str, enum.Enum):
    """Template category types."""
    REMINDER = "REMINDER"
    VISIT_COMPLETE = "VISIT_COMPLETE"
    ALERT = "ALERT"
    DOCUMENT_UPDATE = "DOCUMENT_UPDATE"
    GENERAL = "GENERAL"


class NotificationTemplate(Base):
    """Notification template database model."""

    __tablename__ = "notification_templates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(255), nullable=False, unique=True, index=True)
    template_type = Column(
        SAEnum(TemplateType, name="template_type_enum"),
        nullable=False,
        index=True,
    )
    subject = Column(String(500), nullable=False)
    message_body = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True, default=list)
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
