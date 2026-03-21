from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.identity import Identity


class IdentityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: str) -> Optional[Identity]:
        stmt = select(Identity).where(Identity.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[Identity]:
        stmt = select(Identity).where(Identity.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[Identity]:
        stmt = select(Identity).where(Identity.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Identity]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Identity)
            .options(
                selectinload(Identity.cards),
                selectinload(Identity.memberships),
                selectinload(Identity.project_permissions),
                # selectinload(Identity.events),
                # selectinload(Identity.card_assignment_history),
            )
            .where(Identity.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Identity]:
        stmt = select(Identity)
        if filters:
            for key, value in filters.items():
                if hasattr(Identity, key):
                    stmt = stmt.where(getattr(Identity, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Identity]:
        stmt = select(Identity).options(
            selectinload(Identity.cards),
            selectinload(Identity.memberships),
            selectinload(Identity.project_permissions),
            # selectinload(Identity.events),
            # selectinload(Identity.card_assignment_history),
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Identity, key):
                    stmt = stmt.where(getattr(Identity, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_identities(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        name: Optional[str] = None,
        all: bool = False,
    ) -> List[Identity]:
        from app.models.membership import Membership

        stmt = select(Identity)

        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.join(Identity.memberships).where(
                Membership.organization_id == organization_id
            )

        if name:
            stmt = stmt.where(Identity.name.ilike(f"%{name}%"))

        if not all:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def list_identities_eager(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        name: Optional[str] = None,
        all: bool = False,
    ) -> List[Identity]:
        from app.models.membership import Membership

        stmt = select(Identity).options(
            selectinload(Identity.cards),
            selectinload(Identity.memberships),
            selectinload(Identity.project_permissions),
            # selectinload(Identity.events),
            # selectinload(Identity.card_assignment_history),
        )

        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.join(Identity.memberships).where(
                Membership.organization_id == organization_id
            )

        if name:
            stmt = stmt.where(Identity.name.ilike(f"%{name}%"))

        if not all:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def create(self, identity: Identity) -> Identity:
        self.db.add(identity)
        await self.db.commit()
        await self.db.refresh(identity)
        return identity

    async def update(self, identity: Identity) -> Identity:
        await self.db.commit()
        await self.db.refresh(identity)
        return identity

    async def delete(self, identity: Identity) -> None:
        await self.db.delete(identity)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Identity)
        await self.db.execute(stmt)
        await self.db.commit()
