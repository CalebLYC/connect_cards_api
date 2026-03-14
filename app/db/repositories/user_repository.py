from typing import Optional, List
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_utils.postgres_utils import PostgresTableOperations


class UserRepository:
    def __init__(self, db: AsyncSession):
        self._db_ops = PostgresTableOperations(db, User)

    async def find_by_id(self, id: str) -> Optional[User]:
        """Find a user by ID.

        Args:
            id (str): ID of the user to find.

        Returns:
            Optional[User]: User object if found, None otherwise.
        """
        doc = await self._db_ops.find_one({"id": id})
        if doc:
            doc.pop("_sa_instance_state", None)
            return User(**doc)
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        doc = await self._db_ops.find_one({"email": email})
        if doc:
            doc.pop("_sa_instance_state", None)
            return User(**doc)
        return None

    async def find_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Find a user by phone number.

        Args:
            phone_number (str): Phone number of the user to find.

        Returns:
            Optional[User]: User object if found, None otherwise.
        """
        doc = await self._db_ops.find_one({"phone_number": phone_number})
        if doc:
            doc.pop("_sa_instance_state", None)
            return User(**doc)
        return None

    async def list_users(
        self, skip: int = 0, limit: Optional[int] = 100, all: bool = False
    ) -> List[User]:
        """List users with optional pagination.

        Args:
            skip (int, optional): Number of users to skip. Defaults to 0.
            limit (Optional[int], optional): Maximum number of users to return. Defaults to 100.
            all (bool, optional): If True, returns all users without pagination. Defaults to False.

        Returns:
            List[User]: List of User objects.
        """
        query = {}
        effective_skip = max(0, skip)
        effective_limit = max(1, limit) if limit is not None else 100

        if all:
            docs = await self._db_ops.find_many(query=query, skip=0, limit=None)
        else:
            docs = await self._db_ops.find_many(
                query=query, skip=effective_skip, limit=effective_limit
            )

        users = []
        for doc in docs:
            doc.pop("_sa_instance_state", None)
            users.append(User(**doc))
        return users

    async def create(self, user: User) -> str:
        """Create a new user in the database.

        Args:
            user (User): User object to create.

        Returns:
            str: ID of the created user.
        """
        user_dict = user.__dict__.copy()
        user_dict.pop("_sa_instance_state", None)
        inserted_id = await self._db_ops.insert_one(user_dict)
        return str(inserted_id)

    async def update(self, id: str, update_data: dict) -> bool:
        """Update a user by ID.

        Args:
            id (str): ID of the user to update.
            update_data (dict): Dictionary of fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        modified_count = await self._db_ops.update_one({"id": id}, update_data)
        return modified_count > 0

    async def delete(self, id: str) -> bool:
        """Delete a user by ID.

        Args:
            id (str): ID of the user to delete.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """
        deleted_count = await self._db_ops.delete_one({"id": id})
        return deleted_count > 0
