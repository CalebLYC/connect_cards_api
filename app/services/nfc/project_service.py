from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import (
    ProjectReadSchema,
    LazyProjectReadSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
)


class ProjectService:
    def __init__(self, project_repos: ProjectRepository):
        self.project_repos = project_repos

    async def get_project(
        self, project_id: str, eager: bool = True
    ) -> Optional[ProjectReadSchema]:
        if eager:
            project = await self.project_repos.find_by_id_eager(project_id)
        else:
            project = await self.project_repos.find_by_id(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        return ProjectReadSchema.model_validate(project)

    async def list_projects(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        name: Optional[str] = None,
        eager: bool = False,
    ) -> List[ProjectReadSchema]:
        if eager:
            projects = await self.project_repos.list_eager(
                skip, limit, organization_id, name
            )
        else:
            projects = await self.project_repos.list(skip, limit, organization_id, name)
        return [ProjectReadSchema.model_validate(p) for p in projects]

    async def create_project(
        self, project_create: ProjectCreateSchema
    ) -> LazyProjectReadSchema:
        try:
            project_model = Project(**project_create.model_dump())
            created = await self.project_repos.create(project_model)
            return LazyProjectReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown organization id",
            )

    async def update_project(
        self, project_id: str, project_update: ProjectUpdateSchema
    ) -> LazyProjectReadSchema:
        try:
            project = await self.project_repos.find_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            update_data = project_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(project, key, value)

            updated = await self.project_repos.update(project)
            return LazyProjectReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown organization id",
            )

    async def delete_project(self, project_id: str) -> None:
        project = await self.project_repos.find_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self.project_repos.delete(project)

    async def delete_all_projects(self) -> None:
        await self.project_repos.delete_all()
