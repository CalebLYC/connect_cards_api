from typing import Optional, List
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.models.role import Role
from fastapi import HTTPException, status

from app.schemas.role_schema import (
    RoleCreateSchema,
    RoleReadSchema,
    RoleUpdateSchema,
    LazyRoleReadSchema,
)


class RoleService:
    def __init__(
        self,
        role_repos: RoleRepository,
        permission_repos: PermissionRepository,
    ):
        self.role_repos = role_repos
        self.permission_repos = permission_repos

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

        # Protection : Empêcher la modification du rôle superadmin
        if role.name == "superadmin":
            # (Seul un superadmin devrait pouvoir faire ça, mais idéalement on ne le modifie pas)
            pass

        update_data = role_update.model_dump(exclude_unset=True)
        if "name" in update_data:
            # Empêcher de renommer un rôle en superadmin ou de renommer le superadmin
            if update_data["name"] == "superadmin" and role.name != "superadmin":
                raise HTTPException(
                    status_code=400, detail="Cannot rename a role to 'superadmin'"
                )
            if role.name == "superadmin" and update_data["name"] != "superadmin":
                raise HTTPException(
                    status_code=400, detail="Cannot rename the 'superadmin' role"
                )

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

        # Protection : Empêcher la suppression du rôle superadmin
        if role.name == "superadmin":
            raise HTTPException(
                status_code=403, detail="Superadmin role cannot be deleted."
            )

        await self.role_repos.delete(role)

    async def delete_all_roles(self) -> None:
        """Delete all roles.

        Raises:
            HTTPException: 400 If there are no roles to delete.

        Returns:
            Bool: True if all roles were successfully deleted, otherwise False.
        """
        await self.role_repos.delete_all()

    async def add_permissions_to_role(
        self, role_id: str, permissions_to_add: List[str]
    ) -> RoleReadSchema:
        """
        Assigns new permissions to an existing role.

        Args:
            role_id (str): The id of the role to update.
            permissions_to_add (List[str]): A list of permission codes to add.

        Returns:
            RoleReadSchema: The updated role.

        Raises:
            HTTPException: If the role is not found or any permission is invalid.
        """

    async def add_permissions_to_role(
        self, role_id: str, permissions_to_add: List[str]
    ) -> RoleReadSchema:
        """Assigns new permissions to an existing role."""
        # Récupérer le rôle
        role = await self.role_repos.find_by_id(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found.")

        # Protection : Limiter la modification du rôle superadmin
        if role.name == "superadmin":
            # (Vérifier si le requérant est superadmin ici)
            pass

        # Valider si toutes les permissions à ajouter existent
        existing_permissions = await self.permission_repos.find_many_by_ids(
            ids=permissions_to_add
        )
        # print(f"Existing permissions: {list(existing_permissions)}")
        existing_permission_ids = {str(p.id) for p in existing_permissions}
        # print(f"Existing permission ids: {list(existing_permission_ids)}")

        invalid_permissions = [
            perm_id
            for perm_id in permissions_to_add
            if perm_id not in existing_permission_ids
        ]
        if invalid_permissions:
            raise HTTPException(
                status_code=400,
                detail=f"Permissions not found: {', '.join(invalid_permissions)}. Please create them first.",
            )

        # Ajouter les permissions à la relation
        for permission in existing_permissions:
            if permission not in role.permissions:
                role.permissions.append(permission)

        # Mettre à jour le rôle dans la base de données
        updated = await self.role_repos.update(role)
        if not updated:
            raise HTTPException(
                status_code=500, detail="Failed to update role permissions."
            )

        # Retourner le rôle mis à jour
        return RoleReadSchema.model_validate(role)

    async def remove_permissions_from_role(
        self, role_id: str, permissions_to_remove: List[str]
    ) -> RoleReadSchema:
        """
        Removes specified permissions from an existing role.

        Args:
            role_id (str): The ID of the role to update.
            permissions_to_remove (List[str]): A list of permission codes to remove.

        Returns:
            RoleReadSchema: The updated role.

        Raises:
            HTTPException: If the role is not found or any permission is invalid.
        """

    async def remove_permissions_from_role(
        self, role_id: str, permissions_to_remove: List[str]
    ) -> RoleReadSchema:
        """Removes specified permissions from an existing role."""
        # Récupérer le rôle
        role = await self.role_repos.find_by_id(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found.")

        # Protection : Empêcher de vider le superadmin
        if role.name == "superadmin":
            pass

        # Retirer les permissions de la relation
        role_permission_ids = {str(p.id) for p in role.permissions}
        for permission_id in permissions_to_remove:
            if permission_id in role_permission_ids:
                role.permissions.remove(
                    next(p for p in role.permissions if str(p.id) == permission_id)
                )

        # Mettre à jour le rôle dans la base de données
        updated = await self.role_repos.update(role)
        if not updated:
            raise HTTPException(
                status_code=500, detail="Failed to update role permissions."
            )

        # Retourner le rôle mis à jour
        return RoleReadSchema.model_validate(role)
