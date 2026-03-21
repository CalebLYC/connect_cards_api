from fastapi import APIRouter, Depends, Query, Path, status
from typing import List

from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_organization_service
from app.schemas.organization_schema import (
    OrganizationReadSchema,
    LazyOrganizationReadSchema,
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
)
from app.services.nfc.organization_service import OrganizationService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[require_permission("organization:own", verify_org=True)],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[OrganizationReadSchema],
    summary="List organizations",
    dependencies=[require_role("admin")],
)
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: OrganizationService = Depends(get_organization_service),
):
    return await service.list_organizations(skip=skip, limit=limit, eager=eager)


@router.get(
    "/{id}", response_model=OrganizationReadSchema, summary="Get organization by ID"
)
async def get_organization(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: OrganizationService = Depends(get_organization_service),
):
    return await service.get_organization(id, eager=eager)


@router.post(
    "/",
    response_model=LazyOrganizationReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
    dependencies=[require_role("admin")],
)
async def create_organization(
    organization_create: OrganizationCreateSchema,
    service: OrganizationService = Depends(get_organization_service),
):
    return await service.create_organization(organization_create)


@router.put(
    "/{id}", response_model=LazyOrganizationReadSchema, summary="Update organization"
)
async def update_organization(
    id: str = Path(..., min_length=24, max_length=36),
    organization_update: OrganizationUpdateSchema = ...,
    service: OrganizationService = Depends(get_organization_service),
):
    return await service.update_organization(id, organization_update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete organization"
)
async def delete_organization(
    id: str = Path(..., min_length=24, max_length=36),
    service: OrganizationService = Depends(get_organization_service),
):
    await service.delete_organization(id)
    return {"detail": "Organization deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all organizations",
    dependencies=[require_role("superadmin")],
)
async def delete_all_organizations(
    service: OrganizationService = Depends(get_organization_service),
):
    await service.delete_all_organizations()
    return {"detail": "All organizations deleted"}
