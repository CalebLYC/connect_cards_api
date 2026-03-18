from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.reader import Reader
from app.repositories.reader_repository import ReaderRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.reader_schema import (
    ReaderReadSchema,
    LazyReaderReadSchema,
    ReaderCreateSchema,
    ReaderUpdateSchema,
)


class ReaderService:
    def __init__(
        self,
        reader_repos: ReaderRepository,
        project_repos: ProjectRepository,
        organization_repos: OrganizationRepository,
    ):
        self.reader_repos = reader_repos
        self.project_repos = project_repos
        self.organization_repos = organization_repos

    async def get_reader(
        self, reader_id: str, eager: bool = True
    ) -> Optional[ReaderReadSchema]:
        if eager:
            reader = await self.reader_repos.find_by_id_eager(reader_id)
        else:
            reader = await self.reader_repos.find_by_id(reader_id)

        if not reader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
            )
        return ReaderReadSchema.model_validate(reader)

    async def list_readers(
        self,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        eager: bool = False,
    ) -> List[ReaderReadSchema]:
        if eager:
            readers = await self.reader_repos.find_many_eager(filters, skip, limit)
        else:
            readers = await self.reader_repos.find_many(filters, skip, limit)
        return [ReaderReadSchema.model_validate(r) for r in readers]

    async def create_reader(
        self, reader_create: ReaderCreateSchema
    ) -> LazyReaderReadSchema:
        try:
            db_reader = await self.reader_repos.find_by_name(reader_create.name)
            if db_reader and db_reader.organization_id == reader_create.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reader already exists",
                )
            project = await self.project_repos.find_by_id(reader_create.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )
            if project.organization_id != reader_create.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project not related to organization",
                )
            reader_model = Reader(**reader_create.model_dump())
            created = await self.reader_repos.create(reader_model)
            return LazyReaderReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown project or organization id",
            )

    async def update_reader(
        self, reader_id: str, reader_update: ReaderUpdateSchema
    ) -> LazyReaderReadSchema:
        reader = await self.reader_repos.find_by_id(reader_id)
        if not reader:
            raise HTTPException(status_code=404, detail="Reader not found")

        """if reader_update.name:
            db_reader = await self.reader_repos.find_by_name(reader_update.name)
            if (
                db_reader
                and db_reader.organization_id == reader.organization_id
                and db_reader.id != reader.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reader already exists",
                )"""

        new_project_id = reader_update.project_id
        new_org_id = reader_update.organization_id

        # Compute the effective IDs after the update (fall back to existing values)
        effective_project_id = new_project_id if new_project_id else reader.project_id
        effective_org_id = new_org_id if new_org_id else reader.organization_id

        # Only validate when at least one of the two FK fields is being changed
        if new_project_id or new_org_id:
            if new_project_id:
                project = await self.project_repos.find_by_id(new_project_id)
                if not project:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found",
                    )

            if new_org_id:
                organization = await self.organization_repos.find_by_id(new_org_id)
                if not organization:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Organization not found",
                    )

            # After resolving both sides, make sure the project still belongs to the org
            effective_project = await self.project_repos.find_by_id(
                effective_project_id
            )
            if effective_project.organization_id != effective_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project does not belong to the organization",
                )

        update_data = reader_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(reader, key, value)

        updated = await self.reader_repos.update(reader)
        return LazyReaderReadSchema.model_validate(updated)

    async def delete_reader(self, reader_id: str) -> None:
        reader = await self.reader_repos.find_by_id(reader_id)
        if not reader:
            raise HTTPException(status_code=404, detail="Reader not found")
        await self.reader_repos.delete(reader)

    async def delete_all_readers(self) -> None:
        await self.reader_repos.delete_all()
