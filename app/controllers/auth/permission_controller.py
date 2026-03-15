# app/controllers/auth/permission_controller.py
from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.service_providers import get_permission_service
from app.schemas.permission_schema import (
    PermissionCreateSchema,
    PermissionReadSchema,
    PermissionUpdateSchema,
)
from app.services.auth.permission_service import PermissionService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[PermissionReadSchema],
    summary="List permissions",
)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(default=False),
    service: PermissionService = Depends(get_permission_service),
):
    """List all permissions with pagination."""
    return await service.list_permissions(skip=skip, limit=limit, all=all)


@router.get("/{id}", response_model=PermissionReadSchema, summary="Get a permission by ID")
async def get_permission(
    id: str = Path(..., min_length=24, max_length=36),
    service: PermissionService = Depends(get_permission_service),
):
    """Get a permission by its ID."""
    return await service.get_permission(id)


@router.post(
    "/",
    response_model=PermissionReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission",
)
async def create_permission(
    permission_create: PermissionCreateSchema,
    service: PermissionService = Depends(get_permission_service),
):
    """Create a new permission."""
    return await service.create_permission(permission_create)


@router.put("/{id}", response_model=PermissionReadSchema, summary="Update a permission by ID")
async def update_permission(
    id: str = Path(..., min_length=24, max_length=36),
    permission_update: PermissionUpdateSchema = ...,
    service: PermissionService = Depends(get_permission_service),
):
    """Update a permission by its ID."""
    return await service.update_permission(id, permission_update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a permission by ID"
)
async def delete_permission(
    id: str = Path(..., min_length=24, max_length=36),
    service: PermissionService = Depends(get_permission_service),
):
    """Delete a permission by its ID."""
    await service.delete_permission(id)
    return {"detail": "Permission deleted"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all permissions")
async def delete_all_permissions(
    service: PermissionService = Depends(get_permission_service),
):
    """Delete all permissions."""
    await service.delete_all_permissions()
    return {"detail": "All permissions deleted"}