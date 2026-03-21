from typing import List
from fastapi import APIRouter, Depends, status, Query, Path

from app.providers.auth_provider import require_permission, require_role
from app.services.nfc.webhook_service import WebhookService
from app.schemas.webhook_schema import (
    WebhookReadSchema,
    WebhookCreateSchema,
    WebhookUpdateSchema,
)
from app.providers.service_providers import get_webhook_service

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
    # dependencies=[require_permission("webhook:manage", verify_org=True)],
)


@router.post(
    "/",
    response_model=WebhookReadSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("webhook:manage", verify_org=True)],
)
async def create_webhook(
    webhook: WebhookCreateSchema,
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.create_webhook(webhook)


@router.get(
    "/",
    response_model=List[WebhookReadSchema],
    dependencies=[require_role("admin")],
)
async def list_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.list_webhooks(skip=skip, limit=limit)


@router.get(
    "/{webhook_id}",
    response_model=WebhookReadSchema,
    dependencies=[require_permission("webhook:read", verify_org=True)],
)
async def get_webhook(
    webhook_id: str = Path(..., min_length=24, max_length=36),
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.get_webhook(webhook_id)


@router.put(
    "/{webhook_id}",
    response_model=WebhookReadSchema,
    dependencies=[require_permission("webhook:manage", verify_org=True)],
)
async def update_webhook(
    webhook_id: str = Path(..., min_length=24, max_length=36),
    webhook_update: WebhookUpdateSchema = ...,
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.update_webhook(webhook_id, webhook_update)


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission("webhook:manage", verify_org=True)],
)
async def delete_webhook(
    webhook_id: str = Path(..., min_length=24, max_length=36),
    service: WebhookService = Depends(get_webhook_service),
):
    await service.delete_webhook(webhook_id)
    return {"detail": "Webhook deleted"}
