from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
import datetime
import uuid

from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.repositories.reader_repository import ReaderRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.event_schema import (
    EventReadSchema,
    LazyEventReadSchema,
    EventCreateSchema,
    EventUpdateSchema,
)
from app.schemas.analytics_schema import (
    DailyScanSchema,
    TopCardSchema,
    DenialRateSchema,
    AnalyticsSummarySchema,
)
from fastapi import BackgroundTasks


from app.services.nfc.event_dispatcher import EventDispatcher


class EventService:
    def __init__(
        self,
        event_repos: EventRepository,
        reader_repos: ReaderRepository,
        project_repos: ProjectRepository,
        event_dispatcher: EventDispatcher = None,
    ):
        self.event_repos = event_repos
        self.reader_repos = reader_repos
        self.project_repos = project_repos
        self.event_dispatcher = event_dispatcher

    async def get_event(
        self, event_id: str, eager: bool = True
    ) -> Optional[EventReadSchema]:
        if eager:
            event = await self.event_repos.find_by_id_eager(event_id)
        else:
            event = await self.event_repos.find_by_id(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        return EventReadSchema.model_validate(event)

    async def list_events(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        event_type: Optional[str] = None,
        eager: bool = False,
    ) -> List[EventReadSchema]:
        if eager:
            events = await self.event_repos.list_eager(
                skip, limit, organization_id, project_id, event_type
            )
        else:
            events = await self.event_repos.list(
                skip, limit, organization_id, project_id, event_type
            )
        return [EventReadSchema.model_validate(e) for e in events]

    async def create_event(
        self,
        event_create: EventCreateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyEventReadSchema:
        try:
            db_reader = await self.reader_repos.find_by_id(event_create.reader_id)
            if not db_reader:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reader not found",
                )
            if db_reader.project_id != event_create.project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reader not related to project",
                )
            event_model = Event(**event_create.model_dump())
            created = await self.event_repos.create(event_model)

            if self.event_dispatcher and background_tasks:
                await self.event_dispatcher.dispatch_event(created, background_tasks)

            return LazyEventReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown card or reader or project id",
            )

    async def update_event(
        self,
        event_id: str,
        event_update: EventUpdateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyEventReadSchema:
        try:
            event = await self.event_repos.find_by_id(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")

            new_reader_id = event_update.reader_id
            new_project_id = event_update.project_id

            # Compute the effective IDs after the update (fall back to existing values)
            effective_reader_id = new_reader_id if new_reader_id else event.reader_id
            effective_project_id = (
                new_project_id if new_project_id else event.project_id
            )

            # Only validate when at least one of the two FK fields is being changed
            if new_reader_id or new_project_id:
                if new_reader_id:
                    reader = await self.reader_repos.find_by_id(new_reader_id)
                    if not reader:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reader not found",
                        )

            if new_project_id:
                project = await self.project_repos.find_by_id(new_project_id)
                if not project:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found",
                    )

            # After resolving both sides, make sure the project still belongs to the org
            effective_reader = await self.reader_repos.find_by_id(effective_reader_id)
            if effective_reader.project_id != effective_project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reader does not belong to the project",
                )

            update_data = event_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(event, key, value)

            updated = await self.event_repos.update(event)

            if self.event_dispatcher and background_tasks:
                await self.event_dispatcher.dispatch_event(updated, background_tasks)

            return LazyEventReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown card or reader or project id",
            )

    async def delete_event(self, event_id: str) -> None:
        event = await self.event_repos.find_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        await self.event_repos.delete(event)

    async def delete_all_events(self) -> None:
        await self.event_repos.delete_all()

    async def get_analytics(
        self,
        organization_id: Optional[Any] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> AnalyticsSummarySchema:
        """Fetch and aggregate analytics for a specific organization or globally."""
        daily_scans_data = await self.event_repos.get_scans_per_day(
            organization_id, start_date, end_date
        )
        top_cards_data = await self.event_repos.get_most_used_cards(organization_id)
        denial_metrics = await self.event_repos.get_denial_metrics(
            organization_id, start_date, end_date
        )

        return AnalyticsSummarySchema(
            organization_id=organization_id
            or uuid.UUID(int=0),  # Placeholder for global
            start_date=start_date or datetime.date.min,
            end_date=end_date or datetime.date.max,
            daily_scans=[
                DailyScanSchema(day=row.day, count=row.count)
                for row in daily_scans_data
            ],
            top_cards=[
                TopCardSchema(
                    card_id=row.card_id, count=row.count, card_name=row.card_name
                )
                for row in top_cards_data
            ],
            denial_metrics=DenialRateSchema(**denial_metrics),
        )

    async def get_system_health(self) -> Dict[str, Any]:
        """Fetch global system health metrics."""
        # Simple placeholder for now, could be expanded
        return {
            "total_events": await self.event_repos.db.scalar(
                select(func.count(Event.id))
            ),
            "status": "healthy",
        }
