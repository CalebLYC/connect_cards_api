from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
import uuid

from app.models.identity_project_permission import IdentityProjectPermission
from app.repositories.identity_project_permission_repository import (
    IdentityProjectPermissionRepository,
)
from app.schemas.identity_project_permission_schema import (
    IdentityProjectPermissionReadSchema,
    LazyIdentityProjectPermissionReadSchema,
    IdentityProjectPermissionCreateSchema,
    IdentityProjectPermissionUpdateSchema,
)


class IdentityProjectPermissionService:
    def __init__(self, permission_repos: IdentityProjectPermissionRepository):
        self.permission_repos = permission_repos

    async def get_permission(
        self, permission_id: str, eager: bool = True
    ) -> Optional[IdentityProjectPermissionReadSchema]:
        if eager:
            permission = await self.permission_repos.find_by_id_eager(permission_id)
        else:
            permission = await self.permission_repos.find_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission record not found",
            )
        return IdentityProjectPermissionReadSchema.model_validate(permission)

    async def list_permissions(
        self,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        eager: bool = False,
    ) -> List[IdentityProjectPermissionReadSchema]:
        if eager:
            permissions = await self.permission_repos.find_many_eager(
                filters, skip, limit
            )
        else:
            permissions = await self.permission_repos.find_many(filters, skip, limit)
        return [
            IdentityProjectPermissionReadSchema.model_validate(p) for p in permissions
        ]

    async def create_permission(
        self, permission_create: IdentityProjectPermissionCreateSchema
    ) -> LazyIdentityProjectPermissionReadSchema:
        try:
            permission_model = IdentityProjectPermission(
                **permission_create.model_dump()
            )
            created = await self.permission_repos.create(permission_model)
            return LazyIdentityProjectPermissionReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity or project id",
            )

    async def update_permission(
        self,
        permission_id: str,
        permission_update: IdentityProjectPermissionUpdateSchema,
    ) -> LazyIdentityProjectPermissionReadSchema:
        try:
            permission = await self.permission_repos.find_by_id(permission_id)
            if not permission:
                raise HTTPException(
                    status_code=404, detail="Permission record not found"
                )

            update_data = permission_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(permission, key, value)

            updated = await self.permission_repos.update(permission)
            return LazyIdentityProjectPermissionReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity or project id",
            )

    async def delete_permission(self, permission_id: str) -> None:
        permission = await self.permission_repos.find_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission record not found")
        await self.permission_repos.delete(permission)

    async def delete_all_permissions(self) -> None:
        await self.permission_repos.delete_all()

    async def disallow_identity(
        self, identity_id: str, project_id: str
    ) -> LazyIdentityProjectPermissionReadSchema:
        """
        Explicitly disallows an identity from a project by setting allowed=False.
        Creates a new record if one does not exist.
        """
        try:
            if isinstance(identity_id, str):
                identity_id = uuid.UUID(identity_id)
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)

            permission = await self.permission_repos.find_by_identity_and_project(
                identity_id, project_id
            )

            if permission:
                permission.allowed = False
                updated = await self.permission_repos.update(permission)
                return LazyIdentityProjectPermissionReadSchema.model_validate(updated)
            else:
                # Create a new "disallow" record
                new_permission = IdentityProjectPermission(
                    identity_id=identity_id, project_id=project_id, allowed=False
                )
                created = await self.permission_repos.create(new_permission)
                return LazyIdentityProjectPermissionReadSchema.model_validate(created)

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid identity_id or project_id",
            )

    async def allow_identity(
        self, identity_id: str, project_id: str
    ) -> LazyIdentityProjectPermissionReadSchema:
        """
        Explicitly allows an identity for a project by setting allowed=True.
        Creates a new record if one does not exist.
        """
        try:
            if isinstance(identity_id, str):
                identity_id = uuid.UUID(identity_id)
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)

            permission = await self.permission_repos.find_by_identity_and_project(
                identity_id, project_id
            )

            if permission:
                permission.allowed = True
                updated = await self.permission_repos.update(permission)
                return LazyIdentityProjectPermissionReadSchema.model_validate(updated)
            else:
                # Create a new "allow" record
                new_permission = IdentityProjectPermission(
                    identity_id=identity_id, project_id=project_id, allowed=True
                )
                created = await self.permission_repos.create(new_permission)
                return LazyIdentityProjectPermissionReadSchema.model_validate(created)

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid identity_id or project_id",
            )
