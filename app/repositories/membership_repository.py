from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.membership import Membership


class MembershipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Membership]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Membership).where(Membership.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Membership]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Membership)
            .options(
                selectinload(Membership.identity),
                selectinload(Membership.organization),
            )
            .where(Membership.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Membership]:
        stmt = select(Membership)
        if filters:
            for key, value in filters.items():
                if hasattr(Membership, key):
                    stmt = stmt.where(getattr(Membership, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Membership]:
        stmt = (
            select(Membership)
            .options(
                selectinload(Membership.identity),
                selectinload(Membership.organization),
            )
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Membership, key):
                    stmt = stmt.where(getattr(Membership, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Membership]:
        stmt = select(Membership).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(self, skip: int = 0, limit: int = 100) -> List[Membership]:
        stmt = (
            select(Membership)
            .options(
                selectinload(Membership.identity),
                selectinload(Membership.organization),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, membership: Membership) -> Membership:
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def create_many(self, memberships: List[Membership]) -> List[Membership]:
        self.db.add_all(memberships)
        await self.db.commit()
        for membership in memberships:
            await self.db.refresh(membership)
        return memberships

    async def update(self, membership: Membership) -> Membership:
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def delete(self, membership: Membership) -> None:
        await self.db.delete(membership)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Membership)
        await self.db.execute(stmt)
        await self.db.commit()
