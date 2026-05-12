"""
Pydantic schemas for Email Notification API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.email_notification import EmailStatus


class EmailSendRequest(BaseModel):
    """Schema for sending an email notification."""
    recipient_email: str = Field(..., max_length=255)
    recipient_name: Optional[str] = Field(None, max_length=255)
    subject: str = Field(..., min_length=1, max_length=500)
    body_html: str = Field(..., min_length=1)
    body_text: Optional[str] = None
    is_html: bool = True
    template_id: Optional[UUID] = None


class EmailNotificationResponse(BaseModel):
    """Schema for email notification response."""
    id: UUID
    recipient_email: str
    recipient_name: Optional[str]
    subject: str
    body_html: str
    body_text: Optional[str]
    is_html: bool
    status: EmailStatus
    retry_count: int
    error_message: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailHistoryResponse(BaseModel):
    """Paginated history response for email notifications."""
    items: List[EmailNotificationResponse]
    total: int
    page: int
    page_size: int
