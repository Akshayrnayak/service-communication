"""
Notification Templates API routes.
CRUD operations for managing reusable notification templates.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import verify_token, require_role, rate_limiter, CurrentUser
from app.models.notification_template import NotificationTemplate
from app.schemas.notification_template import (
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse,
    NotificationTemplateListResponse,
)

router = APIRouter(prefix="/templates", tags=["Notification Templates"])


@router.post(
    "/",
    response_model=NotificationTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification template",
)
async def create_template(
    request: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin", "staff")),
):
    """Create a new notification template."""
    template = NotificationTemplate(
        template_name=request.template_name,
        template_type=request.template_type,
        subject=request.subject,
        message_body=request.message_body,
        variables=request.variables,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


@router.get(
    "/",
    response_model=NotificationTemplateListResponse,
    summary="List notification templates",
)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    template_type: str = Query(None, description="Filter by template type"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated list of notification templates."""
    query = select(NotificationTemplate).order_by(NotificationTemplate.created_at.desc())
    if template_type:
        query = query.where(NotificationTemplate.template_type == template_type)

    count_query = select(func.count()).select_from(NotificationTemplate)
    if template_type:
        count_query = count_query.where(NotificationTemplate.template_type == template_type)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return NotificationTemplateListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get(
    "/{template_id}",
    response_model=NotificationTemplateResponse,
    summary="Get a notification template",
)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get a single notification template by ID."""
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put(
    "/{template_id}",
    response_model=NotificationTemplateResponse,
    summary="Update a notification template",
)
async def update_template(
    template_id: UUID,
    request: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin", "staff")),
):
    """Update an existing notification template."""
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.flush()
    await db.refresh(template)
    return template


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notification template",
)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Delete a notification template."""
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(template)
    await db.flush()
