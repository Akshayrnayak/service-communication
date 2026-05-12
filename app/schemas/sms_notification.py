"""
Pydantic schemas for SMS Notification API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.sms_notification import SMSStatus


class SMSSendRequest(BaseModel):
    """Schema for sending an SMS notification."""
    recipient_phone: str = Field(..., min_length=10, max_length=20)
    recipient_name: Optional[str] = Field(None, max_length=255)
    message_body: str = Field(..., min_length=1, max_length=160)
    template_id: Optional[UUID] = None


class SMSNotificationResponse(BaseModel):
    """Schema for SMS notification response."""
    id: UUID
    recipient_phone: str
    recipient_name: Optional[str]
    message_body: str
    status: SMSStatus
    provider_message_id: Optional[str]
    retry_count: int
    error_message: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SMSHistoryResponse(BaseModel):
    """Paginated history response for SMS notifications."""
    items: List[SMSNotificationResponse]
    total: int
    page: int
    page_size: int
