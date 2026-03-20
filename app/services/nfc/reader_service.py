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
from app.repositories.event_repository import EventRepository
from app.models.event import Event
from app.models.enums.event_type_enum import EventTypeEnum
from app.services.nfc.webhook_service import WebhookService


class ReaderService:
    def __init__(
        self,
        reader_repos: ReaderRepository,
        project_repos: ProjectRepository,
        organization_repos: OrganizationRepository,
        event_repos: EventRepository = None,
        webhook_service: WebhookService = None,
    ):
        self.reader_repos = reader_repos
        self.project_repos = project_repos
        self.organization_repos = organization_repos
        self.event_repos = event_repos
        self.webhook_service = webhook_service

    def _log_event(
        self,
        event_type: EventTypeEnum,
        reader_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        metadata_desc: Optional[Dict[str, Any]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        """
        Helper method to log events and trigger webhooks in the background.
        """
        if not self.event_repos:
            return

        async def _save_and_trigger_event():
            event = Event(
                reader_id=reader_id,
                project_id=project_id,
                event_type=event_type,
                metadata_desc=metadata_desc,
            )
            created_event = await self.event_repos.create(event)

            # Trigger webhooks if service is available
            if self.webhook_service and background_tasks:
                await self.webhook_service.trigger_webhooks(
                    created_event, background_tasks
                )
            elif self.webhook_service:
                import asyncio

                await self.webhook_service.trigger_webhooks(
                    created_event, background_tasks
                )

        if background_tasks:
            background_tasks.add_task(_save_and_trigger_event)
        else:
            import asyncio

            asyncio.create_task(_save_and_trigger_event())

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
        self,
        reader_create: ReaderCreateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyReaderReadSchema:
        try:
            db_reader = await self.reader_repos.find_by_name(reader_create.name)
            if db_reader and db_reader.organization_id == reader_create.organization_id:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "create_reader",
                        "reason": "Reader already exists",
                        "name": reader_create.name,
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reader already exists",
                )
            project = await self.project_repos.find_by_id(reader_create.project_id)
            if not project:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "create_reader",
                        "reason": "Project not found",
                        "project_id": str(reader_create.project_id),
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )
            if project.organization_id != reader_create.organization_id:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "create_reader",
                        "reason": "Project not related to organization",
                        "project_id": str(reader_create.project_id),
                        "organization_id": str(reader_create.organization_id),
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project not related to organization",
                )
            reader_model = Reader(**reader_create.model_dump())
            created = await self.reader_repos.create(reader_model)

            # Log creation
            self._log_event(
                event_type=EventTypeEnum.READER_CREATED,
                reader_id=created.id,
                project_id=created.project_id,
                metadata_desc={
                    "action": "create_reader",
                    "name": created.name,
                    "organization_id": str(created.organization_id),
                },
                background_tasks=background_tasks,
            )

            return LazyReaderReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "create_reader",
                    "reason": "Integrity error. Unknown project or organization id",
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown project or organization id",
            )

    async def update_reader(
        self,
        reader_id: str,
        reader_update: ReaderUpdateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyReaderReadSchema:
        reader = await self.reader_repos.find_by_id(reader_id)
        if not reader:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "update_reader",
                    "reason": "Reader not found",
                    "reader_id": str(reader_id),
                },
                background_tasks=background_tasks,
            )
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
                    # Log failure
                    self._log_event(
                        event_type=EventTypeEnum.ACCESS_DENIED,
                        metadata_desc={
                            "action": "update_reader",
                            "reason": "Project not found",
                            "project_id": str(new_project_id),
                        },
                        background_tasks=background_tasks,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found",
                    )

            if new_org_id:
                organization = await self.organization_repos.find_by_id(new_org_id)
                if not organization:
                    # Log failure
                    self._log_event(
                        event_type=EventTypeEnum.ACCESS_DENIED,
                        metadata_desc={
                            "action": "update_reader",
                            "reason": "Organization not found",
                            "organization_id": str(new_org_id),
                        },
                        background_tasks=background_tasks,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Organization not found",
                    )

            # After resolving both sides, make sure the project still belongs to the org
            effective_project = await self.project_repos.find_by_id(
                effective_project_id
            )
            if effective_project.organization_id != effective_org_id:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "update_reader",
                        "reason": "Project does not belong to the organization",
                        "project_id": str(effective_project_id),
                        "organization_id": str(effective_org_id),
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project does not belong to the organization",
                )

        update_data = reader_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(reader, key, value)

        updated = await self.reader_repos.update(reader)

        # Log configuration changes
        if new_project_id or new_org_id:
            self._log_event(
                event_type=EventTypeEnum.READER_UPDATED,
                reader_id=updated.id,
                project_id=updated.project_id,
                metadata_desc={
                    "action": "update_reader_config",
                    "new_project_id": str(new_project_id) if new_project_id else None,
                    "new_org_id": str(new_org_id) if new_org_id else None,
                    "name": updated.name,
                },
                background_tasks=background_tasks,
            )

        return LazyReaderReadSchema.model_validate(updated)

    async def delete_reader(
        self, reader_id: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        reader = await self.reader_repos.find_by_id(reader_id)
        if not reader:
            raise HTTPException(status_code=404, detail="Reader not found")

        # Log deletion
        self._log_event(
            event_type=EventTypeEnum.READER_DELETED,
            reader_id=reader.id,
            project_id=reader.project_id,
            metadata_desc={"action": "delete_reader", "name": reader.name},
            background_tasks=background_tasks,
        )

        await self.reader_repos.delete(reader)

    async def delete_all_readers(self) -> None:
        await self.reader_repos.delete_all()
