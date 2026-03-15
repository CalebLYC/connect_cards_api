from typing import Optional, List
from app.repositories.identity_repository import IdentityRepository
from app.models.identity import Identity
from app.schemas.identity_schema import IdentityCreateSchema, IdentityUpdateSchema, IdentityReadSchema
from fastapi import HTTPException, status


class IdentityService:
    def __init__(
        self,
        identity_repos: IdentityRepository,
    ):
        self.identity_repos = identity_repos

    async def get_identity(self, identity_id: str) -> Optional[IdentityReadSchema]:
        """Retrieve an identity by its ID.

        Args:
            identity_id (str): The ID of the identity to retrieve.

        Raises:
            HTTPException: 404 If the identity is not found.

        Returns:
            Optional[IdentityReadSchema]: The identity data if found, otherwise None.
        """
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
        self, skip: int = 0, limit: int = 100, all: bool = False
    ) -> List[IdentityReadSchema]:
        """List identities with pagination.

        Args:
            skip (int, optional): Number of identities to skip. Defaults to 0.
            limit (int, optional): Maximum number of identities to return. Defaults to 100.
            all (bool, optional): If True, return all identities without pagination. Defaults to False.
        Returns:
            List[IdentityReadSchema]: A list of identity data schemas.
        """
        identitys = await self.identity_repos.list_identities(skip=skip, limit=limit, all=all)
        return [IdentityReadSchema.model_validate(u) for u in identitys]

    async def create_identity(self, identity_create: IdentityCreateSchema) -> IdentityReadSchema:
        """Create a new identity.

        Args:
            identity_create (IdentityCreateSchema): The identity data to create.

        Raises:
            HTTPException: 400 If the email is already registered.

        Returns:
            IdentityReadSchema: The created identity data.
        """
        existing = await self.identity_repos.find_by_email(identity_create.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        identity_model = Identity(**identity_create.model_dump())
        created = await self.identity_repos.create(identity_model)
        return IdentityReadSchema.model_validate(created)

    async def update_identity(
        self, identity_id: str, identity_update: IdentityUpdateSchema
    ) -> IdentityReadSchema:
        """Update an existing identity.

        Args:
            identity_id (str): The ID of the identity to update.
            identity_update (identityUpdateSchema): The identity data to update.

        Raises:
            HTTPException: 404 Not Found if the identity does not exist.
            HTTPException: 400 Bad Request if the email is already registered.
            HTTPException: 500 Internal Server Error if the update fails.

        Returns:
            IdentityReadSchema: The updated identity data.
        """
        identity = await self.identity_repos.find_by_id(identity_id)
        if not identity:
            raise HTTPException(status_code=404, detail="Identity not found")

        update_data = identity_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.identity_repos.find_by_email(update_data["email"])
            if existing and str(existing.id) != identity_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        for key, value in update_data.items():
            setattr(identity, key, value)
        updated = await self.identity_repos.update(identity)
        if not updated:
            raise HTTPException(status_code=500, detail="Update failed")
        return IdentityReadSchema.model_validate(updated)

    async def verify_identity(self, identity_id: str) -> IdentityReadSchema:
        """Verify a identity's account.

        Args:
            identity_id (str): The ID of the identity to verify.

        Raises:
            HTTPException: 404 If the identity is not found.
            HTTPException: 500 If the verification fails.

        Returns:
            IdentityReadSchema: The updated identity data after verification.
        """
        identity = await self.identity_repos.find_by_id(identity_id)
        if not identity:
            raise HTTPException(status_code=404, detail="Identity not found")

        update_data = {"is_verified": True, "is_active": True}

        success = await self.identity_repos.update(identity_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Identity verification failed")

        updated = await self.identity_repos.find_by_id(identity_id)
        return IdentityReadSchema.model_validate(updated)

    async def delete_identity(self, identity_id: str) -> None:
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
            raise HTTPException(status_code=404, detail="Identity not found")
        success = await self.identity_repos.delete(identity_id)
        if not success:
            raise HTTPException(status_code=500, detail="Delete failed")
        return success
