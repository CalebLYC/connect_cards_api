from typing import Optional, List, Any
from sqlalchemy import select, delete, func, desc, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid
import datetime

from app.models.event import Event


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Event]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Event).where(Event.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Event]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Event)
            .options(
                selectinload(Event.card),
                selectinload(Event.reader),
                selectinload(Event.project),
            )
            .where(Event.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        stmt = select(Event)
        if filters:
            for key, value in filters.items():
                if hasattr(Event, key):
                    stmt = stmt.where(getattr(Event, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        stmt = select(Event).options(
            selectinload(Event.card),
            selectinload(Event.reader),
            selectinload(Event.project),
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Event, key):
                    stmt = stmt.where(getattr(Event, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        from app.models.project import Project

        stmt = select(Event)
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.join(Event.project).where(
                Project.organization_id == organization_id
            )
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            stmt = stmt.where(Event.project_id == project_id)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        from app.models.project import Project

        stmt = select(Event).options(
            selectinload(Event.card),
            selectinload(Event.reader),
            selectinload(Event.project),
        )
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.join(Event.project).where(
                Project.organization_id == organization_id
            )
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            stmt = stmt.where(Event.project_id == project_id)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def create_many(self, events: List[Event]) -> List[Event]:
        self.db.add_all(events)
        await self.db.commit()
        for event in events:
            await self.db.refresh(event)
        return events

    async def update(self, event: Event) -> Event:
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def delete(self, event: Event) -> None:
        await self.db.delete(event)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Event)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_scans_per_day(
        self,
        organization_id: Optional[Any] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> List[Any]:
        from app.models.project import Project

        stmt = select(
            func.cast(Event.created_at, Date).label("day"),
            func.count(Event.id).label("count"),
        )

        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.join(Event.project).where(
                Project.organization_id == organization_id
            )

        if start_date:
            stmt = stmt.where(Event.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Event.created_at <= end_date)

        stmt = stmt.group_by("day").order_by("day")
        result = await self.db.execute(stmt)
        return result.all()

    async def get_most_used_cards(
        self, organization_id: Optional[Any] = None, limit: int = 10
    ) -> List[Any]:
        from app.models.project import Project
        from app.models.card import Card

        stmt = (
            select(
                Event.card_id,
                func.count(Event.id).label("count"),
                Card.uid.label("card_name"),
            )
            .join(Card, Event.card_id == Card.id)
            .group_by(Event.card_id, Card.uid)
        )

        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.join(Event.project).where(
                Project.organization_id == organization_id
            )

        stmt = stmt.order_by(desc("count")).limit(limit)
        result = await self.db.execute(stmt)
        return result.all()

    async def get_denial_metrics(
        self,
        organization_id: Optional[Any] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> dict:
        from app.models.project import Project

        # Count total scans
        base_stmt = select(func.count(Event.id))
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            base_stmt = base_stmt.join(Event.project).where(
                Project.organization_id == organization_id
            )

        if start_date:
            base_stmt = base_stmt.where(Event.created_at >= start_date)
        if end_date:
            base_stmt = base_stmt.where(Event.created_at <= end_date)

        total_scans = await self.db.scalar(base_stmt)

        # Count denied scans
        denied_stmt = base_stmt.where(Event.event_type == "ACCESS_DENIED")
        denied_scans = await self.db.scalar(denied_stmt)

        return {
            "total_scans": total_scans or 0,
            "denied_scans": denied_scans or 0,
            "denial_rate": (
                (denied_scans / total_scans * 100)
                if total_scans and total_scans > 0
                else 0
            ),
        }
