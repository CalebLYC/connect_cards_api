from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.webhook import Webhook


class WebhookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Webhook]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Webhook).where(Webhook.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_webhooks_by_event_type(self, event_type: str) -> List[Webhook]:
        stmt = select(Webhook).where(
            Webhook.event_type == event_type, Webhook.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Webhook]:
        stmt = select(Webhook).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, webhook: Webhook) -> Webhook:
        self.db.add(webhook)
        await self.db.commit()
        await self.db.refresh(webhook)
        return webhook

    async def update(self, webhook: Webhook) -> Webhook:
        await self.db.commit()
        await self.db.refresh(webhook)
        return webhook

    async def delete(self, webhook: Webhook) -> None:
        await self.db.delete(webhook)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Webhook)
        await self.db.execute(stmt)
        await self.db.commit()
