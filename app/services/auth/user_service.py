from typing import Optional, List
from app.core.security import SecurityUtils
from app.db.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema, UserReadSchema
from fastapi import HTTPException, status


class UserService:
    def __init__(
        self,
        user_repos: UserRepository,
    ):
        self.user_repos = user_repos

    async def get_user(self, user_id: str) -> Optional[UserReadSchema]:
        """Retrieve a user by its ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Raises:
            HTTPException: 404 If the user is not found.

        Returns:
            Optional[UserReadSchema]: The user data if found, otherwise None.
        """
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserReadSchema.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserReadSchema:
        """Retrieve a user by its email.

        Args:
            email (str): The email of the user to retrieve.

        Raises:
            HTTPException: 404 If the user is not found.

        Returns:
            UserReadSchema: The user data if found.
        """
        user = await self.user_repos.find_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserReadSchema.model_validate(user)

    async def list_users(
        self, skip: int = 0, limit: int = 100, all: bool = False
    ) -> List[UserReadSchema]:
        """List users with pagination.

        Args:
            skip (int, optional): Number of users to skip. Defaults to 0.
            limit (int, optional): Maximum number of users to return. Defaults to 100.
            all (bool, optional): If True, return all users without pagination. Defaults to False.
        Returns:
            List[UserReadSchema]: A list of user data schemas.
        """
        users = await self.user_repos.list_users(skip=skip, limit=limit, all=all)
        return [UserReadSchema.model_validate(u) for u in users]

    async def create_user(self, user_create: UserCreateSchema) -> UserReadSchema:
        """Create a new user.

        Args:
            user_create (UserCreateSchema): The user data to create.

        Raises:
            HTTPException: 400 If the email is already registered.

        Returns:
            UserReadSchema: The created user data.
        """
        existing = await self.user_repos.find_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = SecurityUtils.hash_password(user_create.password)
        user_model = User(
            **user_create.model_dump(exclude=["password"]), password=hashed_pw
        )
        user_id = await self.user_repos.create(user_model)
        created = await self.user_repos.find_by_id(user_id)
        return UserReadSchema.model_validate(created)

    async def update_user(
        self, user_id: str, user_update: UserUpdateSchema
    ) -> UserReadSchema:
        """Update an existing user.

        Args:
            user_id (str): The ID of the user to update.
            user_update (UserUpdateSchema): The user data to update.

        Raises:
            HTTPException: 404 Not Found if the user does not exist.
            HTTPException: 400 Bad Request if the email is already registered.
            HTTPException: 500 Internal Server Error if the update fails.

        Returns:
            UserReadSchema: _description_
        """
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.user_repos.find_by_email(update_data["email"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        if "password" in update_data:
            update_data["password"] = SecurityUtils.hash_password(
                update_data.pop("password")
            )

        success = await self.user_repos.update(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")

        updated = await self.user_repos.find_by_id(user_id)
        return UserReadSchema.model_validate(updated)

    async def verify_user(self, user_id: str) -> UserReadSchema:
        """Verify a user's account.

        Args:
            user_id (str): The ID of the user to verify.

        Raises:
            HTTPException: 404 If the user is not found.
            HTTPException: 500 If the verification fails.

        Returns:
            UserReadSchema: The updated user data after verification.
        """
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = {"is_verified": True, "is_active": True}

        success = await self.user_repos.update(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="User verification failed")

        updated = await self.user_repos.find_by_id(user_id)
        return UserReadSchema.model_validate(updated)

    async def delete_user(self, user_id: str) -> None:
        """Delete a user by its ID.

        Args:
            user_id (str): The ID of the user to delete.

        Raises:
            HTTPException: 404 If the user is not found.
            HTTPException: 500 If the delete operation fails.

        Returns:
           Bool: True if the user was successfully deleted, False otherwise.
        """
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        success = await self.user_repos.delete(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Delete failed")
        return success
