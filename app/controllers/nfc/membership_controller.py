from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, Path

from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_membership_service
from app.schemas.membership_schema import (
    MembershipReadSchema,
    LazyMembershipReadSchema,
    MembershipCreateSchema,
    MembershipUpdateSchema,
)
from app.services.nfc.membership_service import MembershipService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/memberships",
    tags=["Memberships"],
    dependencies=[require_permission("membership:manage", verify_org=True)],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[MembershipReadSchema],
    summary="List memberships",
    dependencies=[require_permission("membership:read", verify_org=True)],
)
async def list_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_id: Optional[str] = Query(None),
    identity_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    eager: bool = Query(True),
    service: MembershipService = Depends(get_membership_service),
):
    return await service.list_memberships(
        skip=skip,
        limit=limit,
        organization_id=organization_id,
        identity_id=identity_id,
        status=status,
        eager=eager,
    )


@router.get(
    "/{membership_id}",
    response_model=MembershipReadSchema,
    summary="Get membership by ID",
)
async def get_membership(
    membership_id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: MembershipService = Depends(get_membership_service),
):
    return await service.get_membership(membership_id, eager=eager)


@router.post(
    "/",
    response_model=LazyMembershipReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create membership",
)
async def create_membership(
    membership_create: MembershipCreateSchema,
    service: MembershipService = Depends(get_membership_service),
):
    return await service.create_membership(membership_create)


@router.put(
    "/{membership_id}",
    response_model=LazyMembershipReadSchema,
    summary="Update membership",
)
async def update_membership(
    membership_id: str = Path(..., min_length=24, max_length=36),
    membership_update: MembershipUpdateSchema = ...,
    service: MembershipService = Depends(get_membership_service),
):
    return await service.update_membership(membership_id, membership_update)


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete membership",
)
async def delete_membership(
    membership_id: str = Path(..., min_length=24, max_length=36),
    service: MembershipService = Depends(get_membership_service),
):
    await service.delete_membership(membership_id)
    return {"detail": "Membership deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all memberships",
    dependencies=[require_role("superadmin")],
)
async def delete_all_memberships(
    service: MembershipService = Depends(get_membership_service),
):
    await service.delete_all_memberships()
    return {"detail": "All memberships deleted"}
