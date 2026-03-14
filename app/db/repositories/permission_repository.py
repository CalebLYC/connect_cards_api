# app/db/repositories/permission_repository.py
from typing import Optional, List
from app.models.permission import Permission
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_utils.postgres_utils import PostgresTableOperations


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self._db_ops = PostgresTableOperations(db, Permission)

    async def find_by_id(self, id: str) -> Optional[Permission]:
        """Find a permission by ID."""
        doc = await self._db_ops.find_one({"id": id})
        if doc:
            doc.pop("_sa_instance_state", None)
            return Permission(**doc)
        return None

    async def find_by_code(self, code: str) -> Optional[Permission]:
        """Find a permission by code."""
        doc = await self._db_ops.find_one({"code": code})
        if doc:
            doc.pop("_sa_instance_state", None)
            return Permission(**doc)
        return None

    async def list_permissions(
        self, skip: int = 0, limit: Optional[int] = 100, all: bool = False
    ) -> List[Permission]:
        """List permissions with optional pagination."""
        query = {}
        effective_skip = max(0, skip)
        effective_limit = max(1, limit) if limit is not None else 100

        if all:
            docs = await self._db_ops.find_many(query=query, skip=0, limit=None)
        else:
            docs = await self._db_ops.find_many(
                query=query, skip=effective_skip, limit=effective_limit
            )

        permissions = []
        for doc in docs:
            doc.pop("_sa_instance_state", None)
            permissions.append(Permission(**doc))
        return permissions

    async def create(self, permission: Permission) -> str:
        """Create a new permission in the database."""
        permission_dict = permission.__dict__.copy()
        permission_dict.pop("_sa_instance_state", None)
        inserted_id = await self._db_ops.insert_one(permission_dict)
        return str(inserted_id)

    async def update(self, id: str, update_data: dict) -> bool:
        """Update a permission by ID."""
        modified_count = await self._db_ops.update_one({"id": id}, update_data)
        return modified_count > 0

    async def delete(self, id: str) -> bool:
        """Delete a permission by ID."""
        deleted_count = await self._db_ops.delete_one({"id": id})
        return deleted_count > 0

    async def delete_by_code(self, code: str) -> bool:
        """Delete a permission by code."""
        deleted_count = await self._db_ops.delete_one({"code": code})
        return deleted_count > 0

    async def delete_all(self) -> bool:
        """Delete all permissions."""
        deleted_count = await self._db_ops.delete_many({})
        return deleted_count > 0
