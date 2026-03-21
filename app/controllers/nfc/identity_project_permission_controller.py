from fastapi import APIRouter, Depends, status, Query, BackgroundTasks, Path
from typing import List, Optional
import uuid

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
from app.providers.auth_provider import require_role, require_permission


router = APIRouter(
    prefix="/identity-project-permissions",
    tags=["Identity Project Permissions"],
    # dependencies=[require_permission("project:permission:manage", verify_org=True)],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[IdentityProjectPermissionReadSchema],
    summary="List permissions",
    dependencies=[require_permission("project:permission:read", verify_org=True)],
)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_id: Optional[str] = Query(None),
    identity_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    eager: bool = Query(True),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    return await service.list_permissions(
        skip=skip,
        limit=limit,
        organization_id=organization_id,
        identity_id=identity_id,
        project_id=project_id,
        eager=eager,
    )


@router.get(
    "/{identity_project_permission_id}",
    response_model=IdentityProjectPermissionReadSchema,
    summary="Get permission by ID",
    dependencies=[require_permission("project:permission:read", verify_org=True)],
)
async def get_identity_project_permission(
    identity_project_permission_id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
):
    return await service.get_identity_project_permission(
        identity_project_permission_id, eager=eager
    )


@router.post(
    "/",
    response_model=LazyIdentityProjectPermissionReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
    dependencies=[require_role("admin")],
)
async def create_permission(
    permission_create: IdentityProjectPermissionCreateSchema,
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
    background_tasks: BackgroundTasks = None,
):
    return await service.create_permission(
        permission_create, background_tasks=background_tasks
    )


@router.put(
    "/{identity_project_permission_id}",
    response_model=LazyIdentityProjectPermissionReadSchema,
    summary="Update permission",
    dependencies=[require_role("admin")],
)
async def update_identity_project_permission(
    identity_project_permission_id: str = Path(..., min_length=24, max_length=36),
    permission_update: IdentityProjectPermissionUpdateSchema = ...,
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
    background_tasks: BackgroundTasks = None,
):
    return await service.update_identity_project_permission(
        identity_project_permission_id,
        permission_update,
        background_tasks=background_tasks,
    )


@router.delete(
    "/{identity_project_permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete permission",
    dependencies=[require_role("admin")],
)
async def delete_identity_project_permission(
    identity_project_permission_id: str = Path(..., min_length=24, max_length=36),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
    background_tasks: BackgroundTasks = None,
):
    await service.delete_identity_project_permission(
        identity_project_permission_id, background_tasks=background_tasks
    )
    return {"detail": "Permission deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all permissions",
    dependencies=[require_role("superadmin")],
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
    dependencies=[require_permission("project:permission:manage", verify_org=True)],
)
async def disallow_identity(
    identity_id: uuid.UUID = Query(...),
    project_id: uuid.UUID = Query(...),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
    background_tasks: BackgroundTasks = None,
):
    """
    Explicitly revoke access for an identity to a project.
    """
    return await service.disallow_identity(
        identity_id, project_id, background_tasks=background_tasks
    )


@router.post(
    "/allow",
    response_model=LazyIdentityProjectPermissionReadSchema,
    summary="Allow identity for project",
    dependencies=[require_permission("project:permission:manage", verify_org=True)],
)
async def allow_identity(
    identity_id: uuid.UUID = Query(...),
    project_id: uuid.UUID = Query(...),
    service: IdentityProjectPermissionService = Depends(
        get_identity_project_permission_service
    ),
    background_tasks: BackgroundTasks = None,
):
    """
    Explicitly grant access for an identity to a project.
    """
    return await service.allow_identity(
        identity_id, project_id, background_tasks=background_tasks
    )
