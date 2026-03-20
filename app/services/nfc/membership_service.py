from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.membership import Membership
from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership_schema import (
    MembershipReadSchema,
    LazyMembershipReadSchema,
    MembershipUpdateSchema,
)
from app.repositories.event_repository import EventRepository
from app.models.event import Event
from app.models.enums.event_type_enum import EventTypeEnum
from fastapi import BackgroundTasks


class MembershipService:
    def __init__(
        self,
        membership_repos: MembershipRepository,
        event_repos: EventRepository = None,
    ):
        self.membership_repos = membership_repos
        self.event_repos = event_repos

    def _log_event(
        self,
        event_type: EventTypeEnum,
        identity_id: Optional[Any] = None,
        metadata_desc: Optional[Dict[str, Any]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        """
        Helper method to log events in the background for performance.
        """
        if not self.event_repos:
            return

        async def _save_event():
            event = Event(
                # Store organization context in metadata if needed
                # identity_id mapping might be useful but we don't have direct FK in Event yet
                event_type=event_type,
                metadata_desc=metadata_desc,
            )
            await self.event_repos.create(event)

        if background_tasks:
            background_tasks.add_task(_save_event)
        else:
            import asyncio

            asyncio.create_task(_save_event())

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
        self,
        membership_create: MembershipCreateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyMembershipReadSchema:
        try:
            membership_model = Membership(**membership_create.model_dump())
            created = await self.membership_repos.create(membership_model)

            # Log creation
            self._log_event(
                event_type=EventTypeEnum.MEMBERSHIP_CREATED,
                identity_id=created.identity_id,
                metadata_desc={
                    "action": "create_membership",
                    "identity_id": str(created.identity_id),
                    "organization_id": str(created.organization_id),
                    "status": created.status,
                },
                background_tasks=background_tasks,
            )

            return LazyMembershipReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "create_membership",
                    "reason": "Data integrity error or duplicate membership",
                    "identity_id": str(membership_create.identity_id),
                    "organization_id": str(membership_create.organization_id),
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error. Unknown identity or organization id. Or membership already exists",
            )

    async def update_membership(
        self,
        membership_id: str,
        membership_update: MembershipUpdateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyMembershipReadSchema:
        try:
            membership = await self.membership_repos.find_by_id(membership_id)
            if not membership:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "update_membership",
                        "reason": "Membership not found",
                        "membership_id": str(membership_id),
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(status_code=404, detail="Membership not found")

            update_data = membership_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(membership, key, value)

            updated = await self.membership_repos.update(membership)

            # Log status changes
            if membership_update.status:
                self._log_event(
                    event_type=EventTypeEnum.MEMBERSHIP_UPDATED,
                    identity_id=updated.identity_id,
                    metadata_desc={
                        "action": "update_membership_status",
                        "status": updated.status,
                        "identity_id": str(updated.identity_id),
                        "organization_id": str(updated.organization_id),
                    },
                    background_tasks=background_tasks,
                )

            return LazyMembershipReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "update_membership",
                    "reason": "Integrity error",
                    "membership_id": str(membership_id),
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity or organization id",
            )

    async def delete_membership(
        self, membership_id: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        membership = await self.membership_repos.find_by_id(membership_id)
        if not membership:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "delete_membership",
                    "reason": "Membership not found",
                    "membership_id": str(membership_id),
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=404, detail="Membership not found")

        # Log deletion
        self._log_event(
            event_type=EventTypeEnum.MEMBERSHIP_DELETED,
            identity_id=membership.identity_id,
            metadata_desc={
                "action": "delete_membership",
                "identity_id": str(membership.identity_id),
                "organization_id": str(membership.organization_id),
            },
            background_tasks=background_tasks,
        )

        await self.membership_repos.delete(membership)

    async def delete_all_memberships(self) -> None:
        await self.membership_repos.delete_all()
