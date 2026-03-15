from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.service_providers import get_identity_service
from app.schemas.identity_schema import IdentityCreateSchema, IdentityUpdateSchema, IdentityReadSchema
from app.services.auth.identity_service import IdentityService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/identities",
    tags=["Identities"],
    dependencies=[],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[IdentityReadSchema],
    summary="List identities",
)
async def list_identitys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(default=False),
    service: IdentityService = Depends(get_identity_service),
):
    """List all identities with pagination.

    Args:
        skip (int, optional): Number of identities to skip. Defaults to Query(0, ge=0).
        limit (int, optional): Maximum number of identities to return. Defaults to Query(100, ge=1, le=1000).
        all (bool, optional): If True, return all identities without pagination. Defaults to Query(default=False).
        service (identityService, optional): identity service dependency.

    Returns:
        List[IdentityReadSchema]: A list of identities, either paginated or all identities if `all` is True.
    """
    return await service.list_identitys(skip=skip, limit=limit, all=all)


@router.get("/{id}", response_model=IdentityReadSchema, summary="Get a identity by ID")
async def get_identity(
    id: str = Path(..., min_length=24, max_length=36),
    service: IdentityService = Depends(get_identity_service),
):
    """Get an identity by its ID.

    Args:
        id (str, optional): The ID of the identity to retrieve. Must be a valid length.
        service (IdentityService, optional): Identity service dependency.

    Raises:
        HTTPException: 404 If the identity with the specified ID does not exist.

    Returns:
        identityReadSchema: The identity's data validated against the identityReadSchema.
    """
    return await service.get_identity(id)


@router.post(
    "/",
    response_model=IdentityReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new identity",
)
async def create_identity(
    identity_create: IdentityCreateSchema,
    service: IdentityService = Depends(get_identity_service),
):
    """Create a new identity.

    Args:
        identity_create (IdentityCreateSchema): The identity data to create, validated against the IdentityCreateSchema.
        service (IdentityService, optional): Identity service dependency.

    Returns:
        IdentityReadSchema: The created identity's data validated against the IdentityReadSchema.
    """
    return await service.create_identity(identity_create)


@router.put("/{id}", response_model=IdentityReadSchema, summary="Update a identity by ID")
async def update_identity(
    id: str = Path(..., min_length=24, max_length=36),
    identity_update: IdentityUpdateSchema = ...,
    service: IdentityService = Depends(get_identity_service),
):
    """Update an identity by its ID.

    Args:
        id (str, optional): The ID of the identity to update. Must be a valid length.
        identity_update (IdentityUpdateSchema, optional): The identity data to update, validated against the IdentityUpdateSchema.
        service (IdentityService, optional): Identity service dependency.

    Returns:
        IdentityReadSchema: The updated identity's data validated against the IdentityReadSchema.
    """
    return await service.update_identity(id, identity_update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an identity by ID"
)
async def delete_identity(
    id: str = Path(..., min_length=24, max_length=36),
    service: IdentityService = Depends(get_identity_service),
):
    """Delete an identity by its ID.

    Args:
        id (str, optional): The ID of the identity to delete. Must be a valid length.
        service (IdentityService, optional): Identity service dependency.

    Returns:
        Bool: A confirmation message indicating the identity was deleted.
    """
    await service.delete_identity(id)
    return {"detail": "Identity deleted"}
