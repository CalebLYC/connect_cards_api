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

    async def get_active_webhooks(
        self, event_type: str, organization_id: Any, project_id: Optional[Any] = None
    ) -> List[Webhook]:
        stmt = select(Webhook).where(
            Webhook.event_type == event_type,
            Webhook.is_active == True,
            Webhook.organization_id == organization_id,
        )
        # Webhook either triggers for the specific project OR triggers site-wide (project_id is Null)
        if project_id:
            stmt = stmt.where(
                (Webhook.project_id.is_(None)) | (Webhook.project_id == project_id)
            )
        else:
            stmt = stmt.where(Webhook.project_id.is_(None))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        is_active: Optional[bool] = None,
    ) -> List[Webhook]:
        stmt = select(Webhook)
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.where(Webhook.organization_id == organization_id)
        if is_active is not None:
            stmt = stmt.where(Webhook.is_active == is_active)

        stmt = stmt.offset(skip).limit(limit)
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
