from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.auth_provider import require_permission
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
    # dependencies=[require_permission("membership:manage")],
    responses=http_status.router_responses,
)


@router.get("/", response_model=List[MembershipReadSchema], summary="List memberships")
async def list_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: MembershipService = Depends(get_membership_service),
):
    return await service.list_memberships(skip=skip, limit=limit, eager=eager)


@router.get(
    "/{id}", response_model=MembershipReadSchema, summary="Get membership by ID"
)
async def get_membership(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: MembershipService = Depends(get_membership_service),
):
    return await service.get_membership(id, eager=eager)


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
    "/{id}", response_model=LazyMembershipReadSchema, summary="Update membership"
)
async def update_membership(
    id: str = Path(..., min_length=24, max_length=36),
    membership_update: MembershipUpdateSchema = ...,
    service: MembershipService = Depends(get_membership_service),
):
    return await service.update_membership(id, membership_update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete membership"
)
async def delete_membership(
    id: str = Path(..., min_length=24, max_length=36),
    service: MembershipService = Depends(get_membership_service),
):
    await service.delete_membership(id)
    return {"detail": "Membership deleted"}


@router.delete(
    "/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all memberships"
)
async def delete_all_memberships(
    service: MembershipService = Depends(get_membership_service),
):
    await service.delete_all_memberships()
    return {"detail": "All memberships deleted"}
