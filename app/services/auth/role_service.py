from typing import Optional, List
from app.repositories.role_repository import RoleRepository
from app.models.role import Role
from fastapi import HTTPException, status

from app.schemas.role_schema import RoleCreateSchema, RoleReadSchema, RoleUpdateSchema, LazyRoleReadSchema

class RoleService:
    def __init__(
        self,
        role_repos: RoleRepository,
    ):
        self.role_repos = role_repos

    async def get_role(self, role_id: str) -> Optional[RoleReadSchema]:
        """Retrieve a role by its ID.

        Args:
            role_id (str): The ID of the role to retrieve.

        Raises:
            HTTPException: 404 If the role is not found.

        Returns:
            Optional[RoleReadSchema]: The role data if found, otherwise None.
        """
        role = await self.role_repos.find_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return RoleReadSchema.model_validate(role)

    async def get_role_by_name(self, name: str) -> Optional[RoleReadSchema]:
        """Retrieve a role by its name.

        Args:
            name (str): The name of the role to retrieve.

        Raises:
            HTTPException: 404 If the role is not found.

        Returns:
            Optional[RoleReadSchema]: The role data if found, otherwise None.
        """
        role = await self.role_repos.find_by_name(name)
        if role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return RoleReadSchema.model_validate(role)

    async def list_roles(
        self, skip: int = 0, limit: int = 100, all: bool = False
    ) -> List[RoleReadSchema]:
        """List roles with pagination.

        Args:
            skip (int, optional): Number of roles to skip. Defaults to 0.
            limit (int, optional): Maximum number of roles to return. Defaults to 100.
            all (bool, optional): If True, return all roles without pagination. Defaults to False.

        Returns:
            List[RoleReadSchema]: A list of role data schemas.
        """
        roles = await self.role_repos.list_roles(skip=skip, limit=limit, all=all)
        return [RoleReadSchema.model_validate(r) for r in roles]

    async def create_role(self, role_create: RoleCreateSchema) -> LazyRoleReadSchema:
        """Create a new role.

        Args:
            role_create (RoleCreateSchema): The role data to create.

        Raises:
            HTTPException: 400 If the role already exists.

        Returns:
            LazyRoleReadSchema: The created role data.
        """
        existing = await self.role_repos.find_by_name(role_create.name)
        if existing:
            raise HTTPException(status_code=400, detail="Role already added")

        role_model = Role(**role_create.model_dump(exclude=["id"]))
        created = await self.role_repos.create(role_model)
        return LazyRoleReadSchema.model_validate(created)

    async def update_role(
        self, role_id: str, role_update: RoleUpdateSchema
    ) -> LazyRoleReadSchema:
        """Update an existing role.

        Args:
            role_id (str): The ID of the role to update.
            role_update (RoleUpdateSchema): The role data to update.

        Raises:
            HTTPException: 404 If the role is not found.
            HTTPException: 400 If the updated role name already exists.
            HTTPException: 500 If the update operation fails.

        Returns:
            LazyRoleReadSchema: The updated role data.
        """
        role = await self.role_repos.find_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        update_data = role_update.model_dump(exclude_unset=True)
        if "name" in update_data:
            existing = await self.role_repos.find_by_name(update_data["name"])
            if existing and str(existing.id) != role_id:
                raise HTTPException(status_code=400, detail="Role already added")

        for key, value in update_data.items():
            setattr(role, key, value)
        updated = await self.role_repos.update(role)
        if not updated:
            raise HTTPException(status_code=500, detail="Update failed")
        return RoleReadSchema.model_validate(updated)

    async def delete_role(self, role_id: str) -> None:
        """Delete a role by its ID.

        Args:
            role_id (str): The ID of the role to delete.

        Raises:
            HTTPException: 404 If the role is not found.
            HTTPException: 500 If the delete operation fails.

        Returns:
            Bool: True if the delete operation was successful, otherwise False.
        """
        role = await self.role_repos.find_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        await self.role_repos.delete(role)

    async def delete_all_roles(self) -> None:
        """Delete all roles.

        Raises:
            HTTPException: 400 If there are no roles to delete.

        Returns:
            Bool: True if all roles were successfully deleted, otherwise False.
        """
        await self.role_repos.delete_all()
