"""
Pydantic schemas for WhatsApp Notification API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.whatsapp_notification import WhatsAppStatus


class WhatsAppSendRequest(BaseModel):
    """Schema for sending a WhatsApp notification."""
    recipient_phone: str = Field(..., min_length=10, max_length=20)
    recipient_name: Optional[str] = Field(None, max_length=255)
    message_body: str = Field(..., min_length=1, max_length=4096)
    template_id: Optional[UUID] = None


class WhatsAppNotificationResponse(BaseModel):
    """Schema for WhatsApp notification response."""
    id: UUID
    recipient_phone: str
    recipient_name: Optional[str]
    message_body: str
    status: WhatsAppStatus
    provider_message_id: Optional[str]
    retry_count: int
    error_message: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WhatsAppHistoryResponse(BaseModel):
    """Paginated history response for WhatsApp notifications."""
    items: List[WhatsAppNotificationResponse]
    total: int
    page: int
    page_size: int
