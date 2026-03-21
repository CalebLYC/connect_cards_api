from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from typing import List

from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_identity_service
from app.schemas.identity_schema import (
    IdentityReadSchema,
    LazyIdentityReadSchema,
    IdentityCreateSchema,
    IdentityUpdateSchema,
)
from app.services.nfc.identity_service import IdentityService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/identities",
    tags=["Identities"],
    dependencies=[require_permission("identity:manage", verify_org=True)],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[IdentityReadSchema],
    summary="List identities",
    dependencies=[require_role("admin")],
)
async def list_identities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(False),
    eager: bool = Query(True),
    service: IdentityService = Depends(get_identity_service),
):
    return await service.list_identitys(skip=skip, limit=limit, all=all, eager=eager)


@router.get("/{id}", response_model=IdentityReadSchema, summary="Get identity by ID")
async def get_identity(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: IdentityService = Depends(get_identity_service),
):
    return await service.get_identity(id, eager=eager)


@router.post(
    "/",
    response_model=LazyIdentityReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create identity",
)
async def create_identity(
    identity_create: IdentityCreateSchema,
    service: IdentityService = Depends(get_identity_service),
    background_tasks: BackgroundTasks = None,
):
    return await service.create_identity(
        identity_create, background_tasks=background_tasks
    )


@router.put("/{id}", response_model=LazyIdentityReadSchema, summary="Update identity")
async def update_identity(
    id: str = Path(..., min_length=24, max_length=36),
    identity_update: IdentityUpdateSchema = ...,
    service: IdentityService = Depends(get_identity_service),
    background_tasks: BackgroundTasks = None,
):
    return await service.update_identity(
        id, identity_update, background_tasks=background_tasks
    )


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete identity"
)
async def delete_identity(
    id: str = Path(..., min_length=24, max_length=36),
    service: IdentityService = Depends(get_identity_service),
    background_tasks: BackgroundTasks = None,
):
    await service.delete_identity(id, background_tasks=background_tasks)
    return {"detail": "Identity deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all identities",
    dependencies=[require_role("superadmin")],
)
async def delete_all_identities(
    service: IdentityService = Depends(get_identity_service),
):
    await service.delete_all_identities()
    return {"detail": "All identities deleted"}
