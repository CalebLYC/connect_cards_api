from typing import Optional, List
from app.repositories.identity_repository import IdentityRepository
from app.models.identity import Identity
from app.schemas.identity_schema import (
    IdentityCreateSchema,
    IdentityUpdateSchema,
    IdentityReadSchema,
    LazyIdentityReadSchema,
)
from fastapi import HTTPException, status, BackgroundTasks
from app.services.nfc.event_dispatcher import EventDispatcher


class IdentityService:
    def __init__(
        self,
        identity_repos: IdentityRepository,
        event_repos: EventRepository = None,
        event_dispatcher: EventDispatcher = None,
    ):
        self.identity_repos = identity_repos
        self.event_repos = event_repos
        self.event_dispatcher = event_dispatcher

    def _log_event(
        self,
        event_type: EventTypeEnum,
        identity_id: Optional[Any] = None,
        metadata_desc: Optional[Dict[str, Any]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        """
        Helper method to log events and trigger webhooks in the background.
        """
        if not self.event_repos:
            return

        async def _save_and_trigger_event():
            event = Event(
                event_type=event_type,
                metadata_desc=metadata_desc,
            )
            created_event = await self.event_repos.create(event)

            # Trigger dispatch if dispatcher is available
            if self.event_dispatcher and background_tasks:
                await self.event_dispatcher.dispatch_event(
                    created_event, background_tasks
                )
            elif self.event_dispatcher:
                import asyncio

                await self.event_dispatcher.dispatch_event(
                    created_event, background_tasks
                )

        if background_tasks:
            background_tasks.add_task(_save_and_trigger_event)
        else:
            import asyncio

            asyncio.create_task(_save_and_trigger_event())

    async def get_identity(
        self, identity_id: str, eager: bool = True
    ) -> Optional[IdentityReadSchema]:
        """Retrieve an identity by its ID.

        Args:
            identity_id (str): The ID of the identity to retrieve.
            eager (bool, optional): If True, use eager loading for relationships. Defaults to True.

        Raises:
            HTTPException: 404 If the identity is not found.

        Returns:
            Optional[IdentityReadSchema]: The identity data if found, otherwise None.
        """
        if eager:
            identity = await self.identity_repos.find_by_id_eager(identity_id)
        else:
            identity = await self.identity_repos.find_by_id(identity_id)

        if not identity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Identity not found"
            )
        return IdentityReadSchema.model_validate(identity)

    async def get_identity_by_email(self, email: str) -> IdentityReadSchema:
        """Retrieve an identity by its email.

        Args:
            email (str): The email of the identity to retrieve.

        Raises:
            HTTPException: 404 If the identity is not found.

        Returns:
            identityReadSchema: The identity data if found.
        """
        identity = await self.identity_repos.find_by_email(email)
        if not identity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Identity not found"
            )
        return IdentityReadSchema.model_validate(identity)

    async def list_identitys(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        name: Optional[str] = None,
        all: bool = False,
        eager: bool = False,
    ) -> List[IdentityReadSchema]:
        """List identities with pagination.

        Args:
            skip (int, optional): Number of identities to skip. Defaults to 0.
            limit (int, optional): Maximum number of identities to return. Defaults to 100.
            organization_id (Optional[Any]): Filter by organization id.
            name (Optional[str]): Filter by name (case-insensitive partial match).
            all (bool, optional): If True, return all identities without pagination. Defaults to False.
            eager (bool, optional): If True, use eager loading for relationships. Defaults to False.
        Returns:
            List[IdentityReadSchema]: A list of identity data schemas.
        """
        if eager:
            identitys = await self.identity_repos.list_identities_eager(
                skip=skip,
                limit=limit,
                organization_id=organization_id,
                name=name,
                all=all,
            )
        else:
            identitys = await self.identity_repos.list_identities(
                skip=skip,
                limit=limit,
                organization_id=organization_id,
                name=name,
                all=all,
            )
        return [IdentityReadSchema.model_validate(u) for u in identitys]

    async def create_identity(
        self,
        identity_create: IdentityCreateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> IdentityReadSchema:
        """Create a new identity.

        Args:
            identity_create (IdentityCreateSchema): The identity data to create.

        Raises:
            HTTPException: 400 If the email is already registered.

        Returns:
            LazyIdentityReadSchema: The created identity data.
        """
        existing = await self.identity_repos.find_by_email(identity_create.email)
        if existing:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "create_identity",
                    "reason": "Email already registered",
                    "email": identity_create.email,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=400, detail="Email already registered")

        identity_model = Identity(**identity_create.model_dump())
        created = await self.identity_repos.create(identity_model)

        # Log event
        self._log_event(
            event_type=EventTypeEnum.IDENTITY_CREATED,
            metadata_desc={
                "action": "create_identity",
                "email": created.email,
                "identity_id": str(created.id),
            },
            background_tasks=background_tasks,
        )

        return LazyIdentityReadSchema.model_validate(created)

    async def update_identity(
        self,
        identity_id: str,
        identity_update: IdentityUpdateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyIdentityReadSchema:
        """Update an existing identity.

        Args:
            identity_id (str): The ID of the identity to update.
            identity_update (identityUpdateSchema): The identity data to update.

        Raises:
            HTTPException: 404 Not Found if the identity does not exist.
            HTTPException: 400 Bad Request if the email is already registered.
            HTTPException: 500 Internal Server Error if the update fails.

        Returns:
            LazyIdentityReadSchema: The updated identity data.
        """
        identity = await self.identity_repos.find_by_id(identity_id)
        if not identity:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "update_identity",
                    "reason": "Identity not found",
                    "identity_id": str(identity_id),
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=404, detail="Identity not found")

        update_data = identity_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.identity_repos.find_by_email(update_data["email"])
            if existing and str(existing.id) != identity_id:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "update_identity",
                        "reason": "Email already registered",
                        "email": update_data["email"],
                        "identity_id": str(identity_id),
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(status_code=400, detail="Email already registered")

        for key, value in update_data.items():
            setattr(identity, key, value)
        updated = await self.identity_repos.update(identity)
        if not updated:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "update_identity",
                    "reason": "Internal update failure",
                    "identity_id": str(identity_id),
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=500, detail="Update failed")

        # Log update
        self._log_event(
            event_type=EventTypeEnum.IDENTITY_UPDATED,
            metadata_desc={
                "action": "update_identity",
                "email": updated.email,
                "identity_id": str(updated.id),
            },
            background_tasks=background_tasks,
        )

        return LazyIdentityReadSchema.model_validate(updated)

    """async def verify_identity(self, identity_id: str) -> LazyIdentityReadSchema:
      Verify a identity's account.

        Args:
            identity_id (str): The ID of the identity to verify.

        Raises:
            HTTPException: 404 If the identity is not found.
            HTTPException: 500 If the verification fails.

        Returns:
            LazyIdentityReadSchema: The updated identity data after verification.
        identity = await self.identity_repos.find_by_id(identity_id)
        if not identity:
            raise HTTPException(status_code=404, detail="Identity not found")

        update_data = {"is_verified": True, "is_active": True}

        success = await self.identity_repos.update(identity_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Identity verification failed")

        updated = await self.identity_repos.find_by_id(identity_id)
        return LazyIdentityReadSchema.model_validate(updated)"""

    async def delete_identity(
        self, identity_id: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Delete a identity by its ID.

        Args:
            identity_id (str): The ID of the identity to delete.

        Raises:
            HTTPException: 404 If the identity is not found.
            HTTPException: 500 If the delete operation fails.

        Returns:
           Bool: True if the identity was successfully deleted, False otherwise.
        """
        identity = await self.identity_repos.find_by_id(identity_id)
        if not identity:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "delete_identity",
                    "reason": "Identity not found",
                    "identity_id": str(identity_id),
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=404, detail="Identity not found")

        # Log event before deletion
        self._log_event(
            event_type=EventTypeEnum.IDENTITY_DELETED,
            metadata_desc={
                "action": "delete_identity",
                "email": identity.email,
                "identity_id": str(identity.id),
            },
            background_tasks=background_tasks,
        )

        success = await self.identity_repos.delete(identity)
        return True

    async def delete_all_identities(self) -> None:
        """Delete all identities."""
        await self.identity_repos.delete_all()
