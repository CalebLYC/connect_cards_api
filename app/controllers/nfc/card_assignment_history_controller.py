from fastapi import APIRouter, Depends, status, Query, Path
from typing import List

from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_card_assignment_history_service
from app.schemas.card_assignment_history_schema import (
    CardAssignmentHistoryReadSchema,
    LazyCardAssignmentHistoryReadSchema,
    CardAssignmentHistoryCreateSchema,
    CardAssignmentHistoryUpdateSchema,
)
from app.services.nfc.card_assignment_history_service import (
    CardAssignmentHistoryService,
)
from app.utils.constants import http_status

router = APIRouter(
    prefix="/card-assignment-histories",
    tags=["Card Assignment Histories"],
    # dependencies=[require_role("superadmin")],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[CardAssignmentHistoryReadSchema],
    summary="List histories",
    dependencies=[require_role("admin")],
)
async def list_histories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: CardAssignmentHistoryService = Depends(
        get_card_assignment_history_service
    ),
):
    return await service.list_histories(skip=skip, limit=limit, eager=eager)


@router.get(
    "/{id}",
    response_model=CardAssignmentHistoryReadSchema,
    summary="Get history by ID",
    dependencies=[require_role("admin")],
)
async def get_history(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: CardAssignmentHistoryService = Depends(
        get_card_assignment_history_service
    ),
):
    return await service.get_history(id, eager=eager)


@router.post(
    "/",
    response_model=LazyCardAssignmentHistoryReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create history record",
    dependencies=[require_role("superadmin")],
)
async def create_history(
    history_create: CardAssignmentHistoryCreateSchema,
    service: CardAssignmentHistoryService = Depends(
        get_card_assignment_history_service
    ),
):
    return await service.create_history(history_create)


@router.put(
    "/{card_assignment_history_id}",
    response_model=LazyCardAssignmentHistoryReadSchema,
    summary="Update history record",
    dependencies=[require_role("superadmin")],
)
async def update_history(
    card_assignment_history_id: str = Path(..., min_length=24, max_length=36),
    history_update: CardAssignmentHistoryUpdateSchema = ...,
    service: CardAssignmentHistoryService = Depends(
        get_card_assignment_history_service
    ),
):
    return await service.update_history(card_assignment_history_id, history_update)


@router.delete(
    "/{card_assignment_history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete history record",
    dependencies=[require_role("superadmin")],
)
async def delete_history(
    card_assignment_history_id: str = Path(..., min_length=24, max_length=36),
    service: CardAssignmentHistoryService = Depends(
        get_card_assignment_history_service
    ),
):
    await service.delete_history(card_assignment_history_id)
    return {"detail": "History record deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all histories",
    dependencies=[require_role("superadmin")],
)
async def delete_all_histories(
    service: CardAssignmentHistoryService = Depends(
        get_card_assignment_history_service
    ),
):
    await service.delete_all_histories()
    return {"detail": "All history records deleted"}
