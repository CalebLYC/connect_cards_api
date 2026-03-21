from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.models.user import User
from app.providers.auth_provider import auth_middleware, require_permission
from app.providers.service_providers import get_user_service
from app.schemas.user_schema import LazyUserReadSchema, UserCreateSchema, UserUpdateSchema, UserReadSchema
from app.services.auth.user_service import UserService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[require_permission("user:manage")],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[UserReadSchema],
    summary="List users",
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(default=False),
    service: UserService = Depends(get_user_service),
):
    """List all users with pagination.

    Args:
        skip (int, optional): Number of users to skip. Defaults to Query(0, ge=0).
        limit (int, optional): Maximum number of users to return. Defaults to Query(100, ge=1, le=1000).
        all (bool, optional): If True, return all users without pagination. Defaults to Query(default=False).
        service (UserService, optional): User service dependency.

    Returns:
        List[UserReadSchema]: A list of users, either paginated or all users if `all` is True.
    """
    return await service.list_users(skip=skip, limit=limit, all=all)


@router.get(
    "/current",
    response_model=UserReadSchema,
    summary="Get the current authenticated user",
)
async def get_current_user(
    current_user: User = Depends(auth_middleware),
):
    """Get the current authenticated user.

    Args:
        current_user (User, optional): The current user from the authentication middleware.

    Returns:
        UserReadSchema: The current user's data validated against the UserReadSchema.
    """
    return UserReadSchema.model_validate(current_user)


@router.get("/{user_id}", response_model=UserReadSchema, summary="Get a user by ID")
async def get_user(
    user_id: str = Path(..., min_length=24, max_length=36),
    service: UserService = Depends(get_user_service),
):
    """Get a user by its ID.

    Args:
        user_id (str, optional): The ID of the user to retrieve. Must be a valid length.
        service (UserService, optional): User service dependency.

    Raises:
        HTTPException: 404 If the user with the specified ID does not exist.

    Returns:
        UserReadSchema: The user's data validated against the UserReadSchema.
    """
    return await service.get_user(user_id)


@router.post(
    "/",
    response_model=LazyUserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_create: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    """Create a new user.

    Args:
        user_create (UserCreateSchema): The user data to create, validated against the UserCreateSchema.
        service (UserService, optional): User service dependency.

    Returns:
        UserReadSchema: The created user's data validated against the UserReadSchema.
    """
    return await service.create_user(user_create)


@router.put("/{user_id}", response_model=LazyUserReadSchema, summary="Update a user by ID")
async def update_user(
    user_id: str = Path(..., min_length=24, max_length=36),
    user_update: UserUpdateSchema = ...,
    service: UserService = Depends(get_user_service),
):
    """Update a user by its ID.

    Args:
        user_id (str, optional): The ID of the user to update. Must be a valid length.
        user_update (UserUpdateSchema, optional): The user data to update, validated against the UserUpdateSchema.
        service (UserService, optional): User service dependency.

    Returns:
        UserReadSchema: The updated user's data validated against the UserReadSchema.
    """
    return await service.update_user(user_id, user_update)


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user by ID"
)
async def delete_user(
    user_id: str = Path(..., min_length=24, max_length=36),
    service: UserService = Depends(get_user_service),
):
    """Delete a user by its ID.

    Args:
        user_id (str, optional): The ID of the user to delete. Must be a valid length.
        service (UserService, optional): User service dependency.

    Returns:
        Bool: A confirmation message indicating the user was deleted.
    """
    await service.delete_user(id)
    return {"detail": "User deleted"}


@router.patch(
    "/{id}/roles",
    response_model=UserReadSchema,
    summary="Add roles to a user",
)
async def add_roles_to_user(
    id: str = Path(..., min_length=24, max_length=36),
    roles_to_add: List[str] = ...,
    service: UserService = Depends(get_user_service),
):
    """Add roles to a user.

    Args:
        id (str, optional): The ID of the user to update. Must be a valid length.
        roles_to_add (List[str], optional): A list of role codes to add.
        service (UserService, optional): User service dependency.

    Returns:
        UserReadSchema: The updated user's data validated against the UserReadSchema.
    """
    return await service.add_roles_to_user(id, roles_to_add)


@router.patch(
    "/{id}/roles/remove",
    response_model=UserReadSchema,
    summary="Remove roles from a user",
)
async def remove_roles_from_user(
    id: str = Path(..., min_length=24, max_length=36),
    roles_to_remove: List[str] = ...,
    service: UserService = Depends(get_user_service),
):
    """Remove roles from a user.

    Args:
        id (str, optional): The ID of the user to update. Must be a valid length.
        roles_to_remove (List[str], optional): A list of role codes to remove.
        service (UserService, optional): User service dependency.

    Returns:
        UserReadSchema: The updated user's data validated against the UserReadSchema.
    """
    return await service.remove_roles_from_user(id, roles_to_remove)


@router.patch(
    "/{id}/permissions",
    response_model=UserReadSchema,
    summary="Add permissions to a user",
)
async def add_permissions_to_user(
    id: str = Path(..., min_length=24, max_length=36),
    permissions_to_add: List[str] = ...,
    service: UserService = Depends(get_user_service),
):
    """Add permissions to a user.

    Args:
        id (str, optional): The ID of the user to update. Must be a valid length.
        permissions_to_add (List[str], optional): A list of permission codes to add.
        service (UserService, optional): User service dependency.

    Returns:
        UserReadSchema: The updated user's data validated against the UserReadSchema.
    """
    return await service.add_permissions_to_user(id, permissions_to_add)


@router.patch(
    "/{id}/permissions/remove",
    response_model=UserReadSchema,
    summary="Remove permissions from a user",
)
async def remove_permissions_from_user(
    id: str = Path(..., min_length=24, max_length=36),
    permissions_to_remove: List[str] = ...,
    service: UserService = Depends(get_user_service),
):
    """Remove permissions from a user.

    Args:
        id (str, optional): The ID of the user to update. Must be a valid length.
        permissions_to_remove (List[str], optional): A list of permission codes to remove.
        service (UserService, optional): User service dependency.

    Returns:
        UserReadSchema: The updated user's data validated against the UserReadSchema.
    """
    return await service.remove_permissions_from_user(id, permissions_to_remove)
