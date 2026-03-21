from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Project]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Project).where(Project.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Project]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Project)
            .options(
                selectinload(Project.organization),
                selectinload(Project.permissions),
                # selectinload(Project.events),
                selectinload(Project.readers),
            )
            .where(Project.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        stmt = select(Project)
        if filters:
            for key, value in filters.items():
                if hasattr(Project, key):
                    stmt = stmt.where(getattr(Project, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.organization),
                selectinload(Project.permissions),
                # selectinload(Project.events),
                selectinload(Project.readers),
            )
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Project, key):
                    stmt = stmt.where(getattr(Project, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        name: Optional[str] = None,
    ) -> List[Project]:
        stmt = select(Project)
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.where(Project.organization_id == organization_id)
        if name:
            stmt = stmt.where(Project.name.ilike(f"%{name}%"))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        name: Optional[str] = None,
    ) -> List[Project]:
        stmt = (
            select(Project).options(
                selectinload(Project.organization),
                selectinload(Project.permissions),
                # selectinload(Project.events),
                selectinload(Project.readers),
            )
        )
        if organization_id:
            if isinstance(organization_id, str):
                organization_id = uuid.UUID(organization_id)
            stmt = stmt.where(Project.organization_id == organization_id)
        if name:
            stmt = stmt.where(Project.name.ilike(f"%{name}%"))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def create_many(self, projects: List[Project]) -> List[Project]:
        self.db.add_all(projects)
        await self.db.commit()
        for project in projects:
            await self.db.refresh(project)
        return projects

    async def update(self, project: Project) -> Project:
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Project)
        await self.db.execute(stmt)
        await self.db.commit()
