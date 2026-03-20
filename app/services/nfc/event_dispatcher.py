import json
from typing import Dict, Any, Optional
from fastapi import BackgroundTasks
from app.models.event import Event
from app.repositories.webhook_repository import WebhookRepository
from app.services.nfc.webhook_service import WebhookService


class EventDispatcher:
    """
    EventDispatcher acts as a central hub for system events.
    It is responsible for identifying interested parties (e.g. webhooks, email services)
    and dispatching the event data to them asynchronously.
    """

    def __init__(
        self, webhook_repos: WebhookRepository, webhook_service: WebhookService
    ):
        self.webhook_repos = webhook_repos
        self.webhook_service = webhook_service

    async def dispatch_event(self, event: Event, background_tasks: BackgroundTasks):
        """
        Main entry point for dispatching an event to all active consumers.
        """
        # 1. Dispatch to Webhooks
        await self._dispatch_to_webhooks(event, background_tasks)

        # 2. Add future dispatchers here (e.g. Slack, Email, etc.)

    async def _dispatch_to_webhooks(
        self, event: Event, background_tasks: BackgroundTasks
    ):
        """
        Internal helper to find and trigger all matching webhooks.
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
            "metadata": event.metadata_desc or {},
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }

        for webhook in webhooks:
            """if background_tasks:
                background_tasks.add_task(
                    self.webhook_service.send_webhook,
                    str(webhook.url),
                    webhook.secret,
                    payload,
                )
            else:"""
            import asyncio

            asyncio.create_task(
                self.webhook_service.send_webhook(
                    str(webhook.url), webhook.secret, payload
                )
            )
