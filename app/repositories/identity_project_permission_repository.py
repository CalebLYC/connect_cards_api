from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.identity_project_permission import IdentityProjectPermission


class IdentityProjectPermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[IdentityProjectPermission]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(IdentityProjectPermission).where(
            IdentityProjectPermission.id == id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[IdentityProjectPermission]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(IdentityProjectPermission)
            .options(
                selectinload(IdentityProjectPermission.identity),
                selectinload(IdentityProjectPermission.project),
            )
            .where(IdentityProjectPermission.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[IdentityProjectPermission]:
        stmt = select(IdentityProjectPermission)
        if filters:
            for key, value in filters.items():
                if hasattr(IdentityProjectPermission, key):
                    stmt = stmt.where(getattr(IdentityProjectPermission, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[IdentityProjectPermission]:
        stmt = select(IdentityProjectPermission).options(
            selectinload(IdentityProjectPermission.identity),
            selectinload(IdentityProjectPermission.project),
        )
        if filters:
            for key, value in filters.items():
                if hasattr(IdentityProjectPermission, key):
                    stmt = stmt.where(getattr(IdentityProjectPermission, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(
        self, skip: int = 0, limit: int = 100
    ) -> List[IdentityProjectPermission]:
        stmt = select(IdentityProjectPermission).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(
        self, skip: int = 0, limit: int = 100
    ) -> List[IdentityProjectPermission]:
        stmt = (
            select(IdentityProjectPermission)
            .options(
                selectinload(IdentityProjectPermission.identity),
                selectinload(IdentityProjectPermission.project),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(
        self, permission: IdentityProjectPermission
    ) -> IdentityProjectPermission:
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def create_many(
        self, permissions: List[IdentityProjectPermission]
    ) -> List[IdentityProjectPermission]:
        self.db.add_all(permissions)
        await self.db.commit()
        for permission in permissions:
            await self.db.refresh(permission)
        return permissions

    async def update(
        self, permission: IdentityProjectPermission
    ) -> IdentityProjectPermission:
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def delete(self, permission: IdentityProjectPermission) -> None:
        await self.db.delete(permission)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(IdentityProjectPermission)
        await self.db.execute(stmt)
        await self.db.commit()

    async def find_by_identity_and_project(
        self, identity_id: uuid.UUID, project_id: uuid.UUID
    ) -> Optional[IdentityProjectPermission]:
        """
        Finds a permission record for a specific identity and project.
        """
        stmt = select(IdentityProjectPermission).where(
            IdentityProjectPermission.identity_id == identity_id,
            IdentityProjectPermission.project_id == project_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
