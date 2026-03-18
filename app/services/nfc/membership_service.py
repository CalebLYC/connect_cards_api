from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.membership import Membership
from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership_schema import (
    MembershipReadSchema,
    LazyMembershipReadSchema,
    MembershipCreateSchema,
    MembershipUpdateSchema,
)


class MembershipService:
    def __init__(self, membership_repos: MembershipRepository):
        self.membership_repos = membership_repos

    async def get_membership(
        self, membership_id: str, eager: bool = True
    ) -> Optional[MembershipReadSchema]:
        if eager:
            membership = await self.membership_repos.find_by_id_eager(membership_id)
        else:
            membership = await self.membership_repos.find_by_id(membership_id)

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found"
            )
        return MembershipReadSchema.model_validate(membership)

    async def list_memberships(
        self,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        eager: bool = False,
    ) -> List[MembershipReadSchema]:
        if eager:
            memberships = await self.membership_repos.find_many_eager(
                filters, skip, limit
            )
        else:
            memberships = await self.membership_repos.find_many(filters, skip, limit)
        return [MembershipReadSchema.model_validate(m) for m in memberships]

    async def create_membership(
        self, membership_create: MembershipCreateSchema
    ) -> LazyMembershipReadSchema:
        try:
            membership_model = Membership(**membership_create.model_dump())
            created = await self.membership_repos.create(membership_model)
            return LazyMembershipReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity or organization id",
            )

    async def update_membership(
        self, membership_id: str, membership_update: MembershipUpdateSchema
    ) -> LazyMembershipReadSchema:
        try:
            membership = await self.membership_repos.find_by_id(membership_id)
            if not membership:
                raise HTTPException(status_code=404, detail="Membership not found")

            update_data = membership_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(membership, key, value)

            updated = await self.membership_repos.update(membership)
            return LazyMembershipReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity or organization id",
            )

    async def delete_membership(self, membership_id: str) -> None:
        membership = await self.membership_repos.find_by_id(membership_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Membership not found")
        await self.membership_repos.delete(membership)

    async def delete_all_memberships(self) -> None:
        await self.membership_repos.delete_all()
