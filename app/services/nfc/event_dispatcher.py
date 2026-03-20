import json
from typing import Dict, Any, Optional
from fastapi import BackgroundTasks
from app.models.event import Event
from app.repositories.webhook_repository import WebhookRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.card_repository import CardRepository
from app.services.nfc.webhook_service import WebhookService


class EventDispatcher:
    """
    EventDispatcher acts as a central hub for system events.
    It is responsible for identifying interested parties (e.g. webhooks, email services)
    and dispatching the event data to them asynchronously.
    """

    def __init__(
        self,
        webhook_repos: WebhookRepository,
        webhook_service: WebhookService,
        project_repos: ProjectRepository = None,
        card_repos: CardRepository = None,
    ):
        self.webhook_repos = webhook_repos
        self.webhook_service = webhook_service
        self.project_repos = project_repos
        self.card_repos = card_repos

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
        project_org_id = None
        card_org_id = None

        # 1. Resolve Project's Organization (Building Owner)
        if event.project_id and self.project_repos:
            project = await self.project_repos.find_by_id(event.project_id)
            if project:
                project_org_id = project.organization_id

        print("Project Org ID:", project_org_id)

        # 2. Resolve Card's Issuer Organization
        if event.card_id and self.card_repos:
            card = await self.card_repos.find_by_id(event.card_id)
            if card:
                card_org_id = card.issuer_organization_id
        elif (
            not event.card_id
            and event.metadata_desc
            and "card_uid" in event.metadata_desc
            and self.card_repos
        ):
            # Fallback for early events like `CARD_SCANNED` where card_id isn't strictly attached yet
            card = await self.card_repos.find_by_uid(event.metadata_desc["card_uid"])
            if card:
                card_org_id = card.issuer_organization_id

        print("Card Org ID:", card_org_id)

        all_webhooks = []

        # A: Trigger Webhooks for the Project Owner (allow scoping to specific project_id or global)
        if project_org_id:
            project_webhooks = await self.webhook_repos.get_active_webhooks(
                event.event_type, project_org_id, event.project_id
            )
            all_webhooks.extend(project_webhooks)

        # B: Trigger Webhooks for the Card Issuer (must be global, as they don't own the project)
        if card_org_id and card_org_id != project_org_id:
            issuer_webhooks = await self.webhook_repos.get_active_webhooks(
                event.event_type, card_org_id, None
            )
            all_webhooks.extend(issuer_webhooks)

        if not all_webhooks:
            print("No webhooks found for event", event)
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

        for webhook in all_webhooks:
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
