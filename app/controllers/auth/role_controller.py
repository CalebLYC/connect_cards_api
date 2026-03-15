from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.service_providers import get_role_service
from app.schemas.role_schema import LazyRoleReadSchema, RoleCreateSchema, RoleReadSchema, RoleUpdateSchema
from app.services.auth.role_service import RoleService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[RoleReadSchema],
    summary="List roles",
)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(default=False),
    service: RoleService = Depends(get_role_service),
):
    """List all roles with pagination.

    Args:
        skip (int, optional): Number of roles to skip. Defaults to Query(0, ge=0).
        limit (int, optional): Maximum number of roles to return. Defaults to Query(100, ge=1, le=1000).
        all (bool, optional): If True, return all roles without pagination. Defaults to Query(default=False).
        service (RoleService, optional): Role service dependency.

    Returns:
        List[RoleReadSchema]: A list of roles, either paginated or all roles if `all` is True.
    """
    return await service.list_roles(skip=skip, limit=limit, all=all)


@router.get("/{id}", response_model=RoleReadSchema, summary="Get a role by ID")
async def get_role(
    id: str = Path(..., min_length=24, max_length=36),
    service: RoleService = Depends(get_role_service),
):
    """Get a role by its ID.

    Args:
        id (str, optional): The ID of the role to retrieve. Must be a valid length.
        service (RoleService, optional): Role service dependency.

    Raises:
        HTTPException: If the role with the specified ID is not found.

    Returns:
        RoleReadSchema: The role's data validated against the RoleReadSchema.
    """
    return await service.get_role(id)


@router.post(
    "/",
    response_model=LazyRoleReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
async def create_role(
    role_create: RoleCreateSchema,
    service: RoleService = Depends(get_role_service),
):
    """Create a new role.

    Args:
        role_create (RoleCreateSchema): The role data to create, validated against the RoleCreateSchema.
        service (RoleService, optional): Role service dependency.

    Returns:
        RoleReadSchema: The created role's data validated against the RoleReadSchema.
    """
    return await service.create_role(role_create)


@router.put("/{id}", response_model=LazyRoleReadSchema, summary="Update a role by ID")
async def update_role(
    id: str = Path(..., min_length=24, max_length=36),
    role_update: RoleUpdateSchema = ...,
    service: RoleService = Depends(get_role_service),
):
    """Update a role by its ID.

    Args:
        id (str, optional): The ID of the role to update. Must be a valid length.
        role_update (RoleUpdateSchema, optional): The role data to update, validated against the RoleUpdateSchema.
        service (RoleService, optional): Role service dependency.

    Returns:
        RoleReadSchema: The updated role's data validated against the RoleReadSchema.
    """
    return await service.update_role(id, role_update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a role by ID"
)
async def delete_role(
    id: str = Path(..., min_length=24, max_length=36),
    service: RoleService = Depends(get_role_service),
):
    """Delete a role by its ID.

    Args:
        id (str, optional): The ID of the role to delete. Must be a valid length.
        service (RoleService, optional): Role service dependency.

    Returns:
        Bool: A confirmation message indicating the role was deleted.
    """
    await service.delete_role(id)
    return {"detail": "Role deleted"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all roles")
async def delete_all_roles(
    service: RoleService = Depends(get_role_service),
):
    """Delete all roles.

    Args:
        service (RoleService, optional): Role service dependency.

    Returns:
        Bool: A confirmation message indicating all roles were deleted.
    """
    await service.delete_all_roles()
    
    
@router.patch(
    "/{id}/permissions",
    response_model=RoleReadSchema,
    summary="Add permissions to a role",
)
async def add_permissions_to_role(
    id: str = Path(..., min_length=24, max_length=36),
    permissions_to_add: List[str] = ...,
    service: RoleService = Depends(get_role_service),
):
    """Add permissions to a role.

    Args:
        id (str, optional): The ID of the role to update. Must be a valid length.
        permissions_to_add (List[str], optional): A list of permission codes to add.
        service (RoleService, optional): Role service dependency.

    Returns:
        RoleReadSchema: The updated role's data validated against the RoleReadSchema.
    """
    return await service.add_permissions_to_role(id, permissions_to_add)


@router.patch(
    "/{id}/permissions/remove",
    response_model=RoleReadSchema,
    summary="Remove permissions from a role",
)
async def remove_permissions_from_role(
    id: str = Path(..., min_length=24, max_length=36),
    permissions_to_remove: List[str] = ...,
    service: RoleService = Depends(get_role_service),
):
    """Remove permissions from a role.

    Args:
        id (str, optional): The ID of the role to update. Must be a valid length.
        permissions_to_remove (List[str], optional): A list of permission codes to remove.
        service (RoleService, optional): Role service dependency.

    Returns:
        RoleReadSchema: The updated role's data validated against the RoleReadSchema.
    """
    return await service.remove_permissions_from_role(id, permissions_to_remove)
