from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def find_by_id(self, id: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def find_by_code(self, code: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def list_permissions(
        self,
        skip: int = 0,
        limit: Optional[int] = 100,
        all: bool = False,
    ) -> List[Permission]:
        stmt = select(Permission)

        if not all:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def create(self, permission: Permission) -> Permission:
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission


    async def update(self, permission: Permission) -> Permission:
        await self.db.commit()
        await self.db.refresh(permission)
        return permission
    

    async def delete(self, permission: Permission) -> None:
        await self.db.delete(permission)
        await self.db.commit()


    async def delete_all(self) -> None:
        stmt = delete(Permission)
        await self.db.execute(stmt)
        await self.db.commit()
