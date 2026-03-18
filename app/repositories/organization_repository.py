from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.organization import Organization


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Organization]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Organization).where(Organization.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Organization]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Organization)
            .options(
                # selectinload(Organization.memberships),
                selectinload(Organization.projects),
                selectinload(Organization.readers),
                selectinload(Organization.users),
                selectinload(Organization.issued_cards),
            )
            .where(Organization.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        stmt = select(Organization)
        if filters:
            for key, value in filters.items():
                if hasattr(Organization, key):
                    stmt = stmt.where(getattr(Organization, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        stmt = (
            select(Organization)
            .options(
                # selectinload(Organization.memberships),
                selectinload(Organization.projects),
                selectinload(Organization.readers),
                selectinload(Organization.users),
                selectinload(Organization.issued_cards),
            )
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Organization, key):
                    stmt = stmt.where(getattr(Organization, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        stmt = select(Organization).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        stmt = (
            select(Organization)
            .options(
                # selectinload(Organization.memberships),
                selectinload(Organization.projects),
                selectinload(Organization.readers),
                selectinload(Organization.users),
                selectinload(Organization.issued_cards),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, organization: Organization) -> Organization:
        self.db.add(organization)
        await self.db.commit()
        await self.db.refresh(organization)
        return organization

    async def create_many(self, organizations: List[Organization]) -> List[Organization]:
        self.db.add_all(organizations)
        await self.db.commit()
        for organization in organizations:
            await self.db.refresh(organization)
        return organizations

    async def update(self, organization: Organization) -> Organization:
        await self.db.commit()
        await self.db.refresh(organization)
        return organization

    async def delete(self, organization: Organization) -> None:
        await self.db.delete(organization)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Organization)
        await self.db.execute(stmt)
        await self.db.commit()
