from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from typing import List

from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_event_service
from app.schemas.event_schema import (
    EventReadSchema,
    LazyEventReadSchema,
    EventCreateSchema,
    EventUpdateSchema,
)
from app.services.nfc.event_service import EventService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    # dependencies=[require_permission("event:manage")],
    # dependencies=[require_role("superadmin")],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[EventReadSchema],
    summary="List events",
    dependencies=[require_role("admin")],
)
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: EventService = Depends(get_event_service),
):
    return await service.list_events(skip=skip, limit=limit, eager=eager)


@router.get(
    "/{id}",
    response_model=EventReadSchema,
    summary="Get event by ID",
    dependencies=[require_role("admin")],
)
async def get_event(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: EventService = Depends(get_event_service),
):
    return await service.get_event(id, eager=eager)


@router.post(
    "/",
    response_model=LazyEventReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    dependencies=[require_role("superadmin")],
)
async def create_event(
    event_create: EventCreateSchema,
    background_tasks: BackgroundTasks,
    service: EventService = Depends(get_event_service),
):
    return await service.create_event(event_create, background_tasks=background_tasks)


@router.put(
    "/{id}",
    response_model=LazyEventReadSchema,
    summary="Update event",
    dependencies=[require_role("superadmin")],
)
async def update_event(
    id: str = Path(..., min_length=24, max_length=36),
    event_update: EventUpdateSchema = ...,
    background_tasks: BackgroundTasks = None,
    service: EventService = Depends(get_event_service),
):
    return await service.update_event(
        id, event_update, background_tasks=background_tasks
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete event",
    dependencies=[require_role("superadmin")],
)
async def delete_event(
    id: str = Path(..., min_length=24, max_length=36),
    service: EventService = Depends(get_event_service),
):
    await service.delete_event(id)
    return {"detail": "Event deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all events",
    dependencies=[require_role("superadmin")],
)
async def delete_all_events(
    service: EventService = Depends(get_event_service),
):
    await service.delete_all_events()
    return {"detail": "All events deleted"}
