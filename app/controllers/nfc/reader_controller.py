from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from typing import List
from app.providers.auth_provider import require_permission
from app.providers.service_providers import get_reader_service
from app.schemas.reader_schema import (
    ReaderReadSchema,
    LazyReaderReadSchema,
    ReaderCreateSchema,
    ReaderUpdateSchema,
)
from app.services.nfc.reader_service import ReaderService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/readers",
    tags=["Readers"],
    # dependencies=[require_permission("reader:manage")],
    responses=http_status.router_responses,
)


@router.get("/", response_model=List[ReaderReadSchema], summary="List readers")
async def list_readers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: ReaderService = Depends(get_reader_service),
):
    return await service.list_readers(skip=skip, limit=limit, eager=eager)


@router.get("/{id}", response_model=ReaderReadSchema, summary="Get reader by ID")
async def get_reader(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: ReaderService = Depends(get_reader_service),
):
    return await service.get_reader(id, eager=eager)


@router.post(
    "/",
    response_model=LazyReaderReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create reader",
)
async def create_reader(
    reader_create: ReaderCreateSchema,
    service: ReaderService = Depends(get_reader_service),
    background_tasks: BackgroundTasks = None,
):
    return await service.create_reader(reader_create, background_tasks=background_tasks)


@router.put("/{id}", response_model=LazyReaderReadSchema, summary="Update reader")
async def update_reader(
    id: str = Path(..., min_length=24, max_length=36),
    reader_update: ReaderUpdateSchema = ...,
    service: ReaderService = Depends(get_reader_service),
    background_tasks: BackgroundTasks = None,
):
    return await service.update_reader(
        id, reader_update, background_tasks=background_tasks
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete reader")
async def delete_reader(
    id: str = Path(..., min_length=24, max_length=36),
    service: ReaderService = Depends(get_reader_service),
    background_tasks: BackgroundTasks = None,
):
    await service.delete_reader(id, background_tasks=background_tasks)
    return {"detail": "Reader deleted"}


@router.delete(
    "/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all readers"
)
async def delete_all_readers(
    service: ReaderService = Depends(get_reader_service),
):
    await service.delete_all_readers()
    return {"detail": "All readers deleted"}
