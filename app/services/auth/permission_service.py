# app/services/auth/permission_service.py
from typing import Optional, List
from app.core.security import SecurityUtils
from app.db.repositories.permission_repository import PermissionRepository
from app.models.permission import Permission
from fastapi import HTTPException, status

from app.schemas.permission_schema import (
    PermissionCreateSchema,
    PermissionReadSchema,
    PermissionUpdateSchema,
)


class PermissionService:
    def __init__(
        self,
        permission_repos: PermissionRepository,
    ):
        self.permission_repos = permission_repos

    async def get_permission(
        self, permission_id: str
    ) -> Optional[PermissionReadSchema]:
        """Retrieve a permission by its ID."""
        permission = await self.permission_repos.find_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        return PermissionReadSchema.model_validate(permission)

    async def get_permission_by_code(self, code: str) -> Optional[PermissionReadSchema]:
        """Retrieve a permission by its code."""
        permission = await self.permission_repos.find_by_code(code)
        if permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        return PermissionReadSchema.model_validate(permission)

    async def list_permissions(
        self, skip: int = 0, limit: int = 100, all: bool = False
    ) -> List[PermissionReadSchema]:
        """List permissions with pagination."""
        permissions = await self.permission_repos.list_permissions(
            skip=skip, limit=limit, all=all
        )
        return [PermissionReadSchema.model_validate(p) for p in permissions]

    async def create_permission(
        self, permission_create: PermissionCreateSchema
    ) -> PermissionReadSchema:
        """Create a new permission."""
        existing = await self.permission_repos.find_by_code(permission_create.code)
        if existing:
            raise HTTPException(status_code=400, detail="Permission already added")

        permission_model = Permission(**permission_create.model_dump(exclude=["id"]))
        permission_id = await self.permission_repos.create(permission_model)
        created = await self.permission_repos.find_by_id(permission_id)
        return PermissionReadSchema.model_validate(created)

    async def update_permission(
        self, permission_id: str, permission_update: PermissionUpdateSchema
    ) -> PermissionReadSchema:
        """Update an existing permission."""
        permission = await self.permission_repos.find_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        update_data = permission_update.model_dump(exclude_unset=True)
        if "code" in update_data:
            existing = await self.permission_repos.find_by_code(update_data["code"])
            if existing and str(existing.id) != permission_id:
                raise HTTPException(status_code=400, detail="Permission already added")

        success = await self.permission_repos.update(permission_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")

        updated = await self.permission_repos.find_by_id(permission_id)
        return PermissionReadSchema.model_validate(updated)

    async def delete_permission(self, permission_id: str) -> None:
        """Delete a permission by its ID."""
        permission = await self.permission_repos.find_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        success = await self.permission_repos.delete(permission_id)
        if not success:
            raise HTTPException(status_code=500, detail="Delete failed")
        return success

    async def delete_all_permissions(self) -> None:
        """Delete all permissions."""
        success = await self.permission_repos.delete_all()
        if not success:
            raise HTTPException(status_code=400, detail="Any permission to delete")
        return success
