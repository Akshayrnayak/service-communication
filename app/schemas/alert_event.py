"""
Pydantic schemas for Alert Event API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.alert_event import AlertType, AlertPriority, AlertStatus


class AlertEventCreate(BaseModel):
    """Schema for creating an emergency alert."""
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.HIGH
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    recipient_id: UUID
    recipient_phone: Optional[str] = Field(None, max_length=20)
    recipient_email: Optional[str] = Field(None, max_length=255)
    channels_used: Optional[str] = "SMS,WHATSAPP,EMAIL"


class AlertEventResponse(BaseModel):
    """Schema for alert event response."""
    id: UUID
    alert_type: AlertType
    priority: AlertPriority
    title: str
    description: str
    recipient_id: UUID
    recipient_phone: Optional[str]
    recipient_email: Optional[str]
    channels_used: str
    status: AlertStatus
    retry_count: int
    escalation_level: int
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertEventListResponse(BaseModel):
    """Paginated list response for alert events."""
    items: List[AlertEventResponse]
    total: int
    page: int
    page_size: int
