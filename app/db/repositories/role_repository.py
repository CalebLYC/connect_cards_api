from typing import Optional, List
from app.models.role import Role
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_utils.postgres_utils import PostgresTableOperations


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self._db_ops = PostgresTableOperations(db, Role)

    async def find_by_id(self, id: str) -> Optional[Role]:
        """Find a role by ID.

        Args:
            id (str): ID of the role to find.

        Returns:
            Optional[Role]: Role object if found, None otherwise.
        """
        doc = await self._db_ops.find_one({"id": id})
        if doc:
            doc.pop("_sa_instance_state", None)
            return Role(**doc)
        return None

    async def find_by_name(self, name: str) -> Optional[Role]:
        """Find a role by name.

        Args:
            name (str): Name of the role to find.

        Returns:
            Optional[Role]: Role object if found, None otherwise.
        """
        doc = await self._db_ops.find_one({"name": name})
        if doc:
            doc.pop("_sa_instance_state", None)
            return Role(**doc)
        return None

    async def list_roles(
        self, skip: int = 0, limit: Optional[int] = 100, all: bool = False
    ) -> List[Role]:
        """List roles with optional pagination.

        Args:
            skip (int, optional): Number of roles to skip. Defaults to 0.
            limit (Optional[int], optional): Maximum number of roles to return. Defaults to 100.
            all (bool, optional): If True, returns all roles without pagination. Defaults to False.

        Returns:
            List[Role]: List of Role objects.
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

        roles = []
        for doc in docs:
            doc.pop("_sa_instance_state", None)
            roles.append(Role(**doc))
        return roles

    async def create(self, user: Role) -> str:
        """Create a new role in the database.

        Args:
            user (Role): Role object to create.

        Returns:
            str: ID of the created role.
        """
        roles_dict = user.__dict__.copy()
        roles_dict.pop("_sa_instance_state", None)
        inserted_id = await self._db_ops.insert_one(roles_dict)
        return str(inserted_id)

    async def update(self, id: str, update_data: dict) -> bool:
        """Update a role by ID.

        Args:
            id (str): ID of the role to update.
            update_data (dict): Dictionary of fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        modified_count = await self._db_ops.update_one({"id": id}, update_data)
        return modified_count > 0

    async def delete(self, id: str) -> bool:
        """Delete a role by ID.

        Args:
            id (str): ID of the role to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        deleted_count = await self._db_ops.delete_one({"id": id})
        return deleted_count > 0

    async def delete_by_name(self, name: str) -> bool:
        """Delete a role by name.

        Args:
            name (str): Name of the role to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        deleted_count = await self._db_ops.delete_one({"name": name})
        return deleted_count > 0

    async def delete_all(self) -> bool:
        """Delete all roles.

        Returns:
            bool: True if all roles were deleted, False otherwise.
        """
        deleted_count = await self._db_ops.delete_many({})
        return deleted_count > 0
