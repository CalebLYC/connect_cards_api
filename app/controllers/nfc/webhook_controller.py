from typing import List
from fastapi import APIRouter, Depends, status, Query
from app.services.nfc.webhook_service import WebhookService
from app.schemas.webhook_schema import (
    WebhookReadSchema,
    WebhookCreateSchema,
    WebhookUpdateSchema,
)
from app.providers.service_providers import get_webhook_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/", response_model=WebhookReadSchema, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook: WebhookCreateSchema,
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.create_webhook(webhook)


@router.get("/", response_model=List[WebhookReadSchema])
async def list_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.list_webhooks(skip=skip, limit=limit)


@router.get("/{id}", response_model=WebhookReadSchema)
async def get_webhook(
    id: str,
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.get_webhook(id)


@router.put("/{id}", response_model=WebhookReadSchema)
async def update_webhook(
    id: str,
    webhook_update: WebhookUpdateSchema,
    service: WebhookService = Depends(get_webhook_service),
):
    return await service.update_webhook(id, webhook_update)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    id: str,
    service: WebhookService = Depends(get_webhook_service),
):
    await service.delete_webhook(id)
    return None
