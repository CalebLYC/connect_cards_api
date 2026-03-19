from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.auth_provider import require_permission
from app.providers.service_providers import get_identity_project_permission_service
from app.schemas.identity_project_permission_schema import (
    IdentityProjectPermissionReadSchema,
    LazyIdentityProjectPermissionReadSchema,
    IdentityProjectPermissionCreateSchema,
    IdentityProjectPermissionUpdateSchema,
)
from app.services.nfc.identity_project_permission_service import (
    IdentityProjectPermissionService,
)
from app.utils.constants import http_status
import uuid

router = APIRouter(
    prefix="/identity-project-permissions",
    tags=["Identity Project Permissions"],
    # dependencies=[require_permission("permission:manage")],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[IdentityProjectPermissionReadSchema],
    summary="List permissions",
)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    return await service.list_permissions(skip=skip, limit=limit, eager=eager)


@router.get(
    "/{id}",
    response_model=IdentityProjectPermissionReadSchema,
    summary="Get permission by ID",
)
async def get_permission(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    return await service.get_permission(id, eager=eager)


@router.post(
    "/",
    response_model=LazyIdentityProjectPermissionReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
)
async def create_permission(
    permission_create: IdentityProjectPermissionCreateSchema,
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    return await service.create_permission(permission_create)


@router.put(
    "/{id}",
    response_model=LazyIdentityProjectPermissionReadSchema,
    summary="Update permission",
)
async def update_permission(
    id: str = Path(..., min_length=24, max_length=36),
    permission_update: IdentityProjectPermissionUpdateSchema = ...,
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    return await service.update_permission(id, permission_update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete permission"
)
async def delete_permission(
    id: str = Path(..., min_length=24, max_length=36),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    await service.delete_permission(id)
    return {"detail": "Permission deleted"}


@router.delete(
    "/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all permissions"
)
async def delete_all_permissions(
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    await service.delete_all_permissions()
    return {"detail": "All permissions deleted"}


@router.post(
    "/disallow",
    response_model=LazyIdentityProjectPermissionReadSchema,
    summary="Disallow identity from project",
)
async def disallow_identity(
    identity_id: uuid.UUID = Query(...),
    project_id: uuid.UUID = Query(...),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    """
    Explicitly revoke access for an identity to a project.
    """
    return await service.disallow_identity(identity_id, project_id)


@router.post(
    "/allow",
    response_model=LazyIdentityProjectPermissionReadSchema,
    summary="Allow identity for project",
)
async def allow_identity(
    identity_id: uuid.UUID = Query(...),
    project_id: uuid.UUID = Query(...),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    """
    Explicitly grant access for an identity to a project.
    """
    return await service.allow_identity(identity_id, project_id)
