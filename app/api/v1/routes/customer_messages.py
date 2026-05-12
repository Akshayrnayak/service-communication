"""
Customer Messages API routes.
Manages all outgoing customer communication records.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import verify_token, CurrentUser
from app.models.customer_message import CustomerMessage
from app.schemas.customer_message import (
    CustomerMessageCreate,
    CustomerMessageResponse,
    CustomerMessageListResponse,
)

router = APIRouter(prefix="/messages", tags=["Customer Messages"])


@router.post(
    "/",
    response_model=CustomerMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a customer message record",
)
async def create_message(
    request: CustomerMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Record a new outgoing customer message."""
    message = CustomerMessage(
        customer_id=request.customer_id,
        customer_name=request.customer_name,
        mobile_number=request.mobile_number,
        email=request.email,
        message_type=request.message_type,
        delivery_channel=request.delivery_channel,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


@router.get(
    "/",
    response_model=CustomerMessageListResponse,
    summary="List customer messages",
)
async def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: UUID = Query(None, description="Filter by customer ID"),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated list of customer messages."""
    query = select(CustomerMessage).order_by(CustomerMessage.created_at.desc())
    if customer_id:
        query = query.where(CustomerMessage.customer_id == customer_id)
    if status_filter:
        query = query.where(CustomerMessage.status == status_filter)

    count_query = select(func.count()).select_from(CustomerMessage)
    if customer_id:
        count_query = count_query.where(CustomerMessage.customer_id == customer_id)
    if status_filter:
        count_query = count_query.where(CustomerMessage.status == status_filter)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return CustomerMessageListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get(
    "/{message_id}",
    response_model=CustomerMessageResponse,
    summary="Get a customer message",
)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get a single customer message by ID."""
    result = await db.execute(
        select(CustomerMessage).where(CustomerMessage.id == message_id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
