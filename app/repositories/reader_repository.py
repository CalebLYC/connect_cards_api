from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.reader import Reader


class ReaderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Reader]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Reader).where(Reader.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Reader]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Reader)
            .options(
                selectinload(Reader.organization),
                selectinload(Reader.project),
                # selectinload(Reader.events),
            )
            .where(Reader.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[Reader]:
        stmt = select(Reader).where(Reader.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Reader]:
        stmt = select(Reader)
        if filters:
            for key, value in filters.items():
                if hasattr(Reader, key):
                    stmt = stmt.where(getattr(Reader, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Reader]:
        stmt = select(Reader).options(
            selectinload(Reader.organization),
            selectinload(Reader.project),
            # selectinload(Reader.events),
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Reader, key):
                    stmt = stmt.where(getattr(Reader, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Reader]:
        stmt = select(Reader)
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.where(Reader.organization_id == organization_id)
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            stmt = stmt.where(Reader.project_id == project_id)
        if name:
            stmt = stmt.where(Reader.name.ilike(f"%{name}%"))
        if status:
            stmt = stmt.where(Reader.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Reader]:
        stmt = select(Reader).options(
            selectinload(Reader.organization),
            selectinload(Reader.project),
            # selectinload(Reader.events),
        )
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.where(Reader.organization_id == organization_id)
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            stmt = stmt.where(Reader.project_id == project_id)
        if name:
            stmt = stmt.where(Reader.name.ilike(f"%{name}%"))
        if status:
            stmt = stmt.where(Reader.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, reader: Reader) -> Reader:
        self.db.add(reader)
        await self.db.commit()
        await self.db.refresh(reader)
        return reader

    async def create_many(self, readers: List[Reader]) -> List[Reader]:
        self.db.add_all(readers)
        await self.db.commit()
        for reader in readers:
            await self.db.refresh(reader)
        return readers

    async def update(self, reader: Reader) -> Reader:
        await self.db.commit()
        await self.db.refresh(reader)
        return reader

    async def delete(self, reader: Reader) -> None:
        await self.db.delete(reader)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Reader)
        await self.db.execute(stmt)
        await self.db.commit()
