import hmac
import hashlib
import json
import httpx
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, BackgroundTasks
import uuid

from app.models.webhook import Webhook
from app.models.event import Event
from app.repositories.webhook_repository import WebhookRepository
from app.schemas.webhook_schema import (
    WebhookCreateSchema,
    WebhookUpdateSchema,
    WebhookReadSchema,
)


class WebhookService:
    def __init__(self, webhook_repos: WebhookRepository):
        self.webhook_repos = webhook_repos

    async def get_webhook(self, webhook_id: str) -> Optional[WebhookReadSchema]:
        webhook = await self.webhook_repos.find_by_id(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return WebhookReadSchema.model_validate(webhook)

    async def list_webhooks(
        self, skip: int = 0, limit: int = 100
    ) -> List[WebhookReadSchema]:
        webhooks = await self.webhook_repos.list(skip, limit)
        return [WebhookReadSchema.model_validate(w) for w in webhooks]

    async def create_webhook(
        self, webhook_create: WebhookCreateSchema
    ) -> WebhookReadSchema:
        webhook_model = Webhook(**webhook_create.model_dump())
        created = await self.webhook_repos.create(webhook_model)
        return WebhookReadSchema.model_validate(created)

    async def update_webhook(
        self, webhook_id: str, webhook_update: WebhookUpdateSchema
    ) -> WebhookReadSchema:
        webhook = await self.webhook_repos.find_by_id(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        update_data = webhook_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(webhook, key, value)

        updated = await self.webhook_repos.update(webhook)
        return WebhookReadSchema.model_validate(updated)

    async def delete_webhook(self, webhook_id: str) -> None:
        webhook = await self.webhook_repos.find_by_id(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        await self.webhook_repos.delete(webhook)

    async def trigger_webhooks(self, event: Event, background_tasks: BackgroundTasks):
        """
        Fetches all active webhooks for the given event type and adds them to background tasks.
        """
        webhooks = await self.webhook_repos.get_active_webhooks_by_event_type(
            event.event_type
        )
        if not webhooks:
            return

        payload = {
            "event_id": str(event.id),
            "event_type": event.event_type,
            "card_id": str(event.card_id) if event.card_id else None,
            "reader_id": str(event.reader_id) if event.reader_id else None,
            "project_id": str(event.project_id) if event.project_id else None,
            "metadata": event.metadata_desc,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }

        for webhook in webhooks:
            # We pass the primitives to background task to avoid DB session issues
            background_tasks.add_task(
                self.send_webhook, str(webhook.url), webhook.secret, payload
            )

    @staticmethod
    async def send_webhook(url: str, secret: Optional[str], payload: Dict[str, Any]):
        """
        Sends a POST request to the webhook URL with an optional HMAC signature.
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ConnectCards-Webhook/1.0",
        }
        body = json.dumps(payload)

        if secret:
            signature = hmac.new(
                secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Hub-Signature-256"] = f"sha256={signature}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, content=body)
                response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Webhook delivery failed to {url}: {e}")
        except Exception as e:
            print(f"Unexpected error during webhook delivery to {url}: {e}")
