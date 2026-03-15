from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException
from uuid import UUID

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def find_by_id(self, id: str):
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def find_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def find_many_by_ids(self, ids: List[str]) -> List[Role]:
        # Validation des UUID
        valid_ids = []
        for uid in ids:
            try:
                valid_ids.append(str(UUID(uid)))  # Convertit en UUID et le retransforme en string
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid UUID: '{uid}'"
                )
    
        stmt = select(Role).where(Role.id.in_(valid_ids))
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def find_many_by_names(self, names: List[str]) -> List[Role]:
        stmt = select(Role).where(Role.name.in_(names))
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def list_roles(
        self,
        skip: int = 0,
        limit: Optional[int] = 100,
        all: bool = False,
    ) -> List[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
        )

        if not all:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role


    async def update(self, role: Role) -> Role:
        await self.db.commit()
        await self.db.refresh(role)
        return role


    async def delete(self, role: Role) -> None:
        await self.db.delete(role)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Role)
        await self.db.execute(stmt)
        await self.db.commit()
