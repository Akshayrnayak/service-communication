"""
Pydantic schemas for Notification Template API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.notification_template import TemplateType


class NotificationTemplateCreate(BaseModel):
    """Schema for creating a notification template."""
    template_name: str = Field(..., min_length=3, max_length=255)
    template_type: TemplateType
    subject: str = Field(..., min_length=1, max_length=500)
    message_body: str = Field(..., min_length=1)
    variables: Optional[List[str]] = Field(default=[])


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating a notification template."""
    template_name: Optional[str] = Field(None, min_length=3, max_length=255)
    template_type: Optional[TemplateType] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    message_body: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None
    is_active: Optional[str] = None


class NotificationTemplateResponse(BaseModel):
    """Schema for notification template response."""
    id: UUID
    template_name: str
    template_type: TemplateType
    subject: str
    message_body: str
    variables: Optional[List[str]]
    is_active: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationTemplateListResponse(BaseModel):
    """Paginated list response for templates."""
    items: List[NotificationTemplateResponse]
    total: int
    page: int
    page_size: int
