from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    

    async def list_identities(
        self,
        skip: int = 0,
        limit: Optional[int] = 100,
        all: bool = False,
    ) -> List[Identity]:

        stmt = select(Identity)

        if not all:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()
    

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
