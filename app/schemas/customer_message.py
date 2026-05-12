"""
Pydantic schemas for Customer Message API validation.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.customer_message import MessageType, DeliveryChannel, MessageStatus


class CustomerMessageCreate(BaseModel):
    """Schema for creating a customer message."""
    customer_id: UUID
    customer_name: str = Field(..., min_length=1, max_length=255)
    mobile_number: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    message_type: MessageType
    delivery_channel: DeliveryChannel


class CustomerMessageResponse(BaseModel):
    """Schema for customer message response."""
    id: UUID
    customer_id: UUID
    customer_name: str
    mobile_number: Optional[str]
    email: Optional[str]
    message_type: MessageType
    delivery_channel: DeliveryChannel
    status: MessageStatus
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerMessageListResponse(BaseModel):
    """Paginated list response for customer messages."""
    items: List[CustomerMessageResponse]
    total: int
    page: int
    page_size: int
