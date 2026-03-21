from typing import Optional, List
from app.core.security import SecurityUtils
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user_schema import (
    LazyUserReadSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserReadSchema,
)
from fastapi import HTTPException, status


class UserService:
    def __init__(
        self,
        user_repos: UserRepository,
        role_repos: Optional[RoleRepository] = None,
        permission_repos: Optional[PermissionRepository] = None,
    ):
        self.user_repos = user_repos
        self.role_repos = role_repos
        self.permission_repos = permission_repos

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
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[Any] = None,
        is_active: Optional[bool] = None,
        role_name: Optional[str] = None,
        all: bool = False,
    ) -> List[UserReadSchema]:
        """List users with pagination.

        Args:
            skip (int, optional): Number of users to skip. Defaults to 0.
            limit (int, optional): Maximum number of users to return. Defaults to 100.
            organization_id (Optional[Any]): Filter by organization id.
            is_active (Optional[bool]): Filter by active status.
            role_name (Optional[str]): Filter by role name.
            all (bool, optional): If True, return all users without pagination. Defaults to False.
        Returns:
            List[UserReadSchema]: A list of user data schemas.
        """
        users = await self.user_repos.list_users(
            skip=skip,
            limit=limit,
            organization_id=organization_id,
            is_active=is_active,
            role_name=role_name,
            all=all,
        )
        return [UserReadSchema.model_validate(u) for u in users]

    async def create_user(self, user_create: UserCreateSchema) -> LazyUserReadSchema:
        """Create a new user.

        Args:
            user_create (UserCreateSchema): The user data to create.

        Raises:
            HTTPException: 400 If the email is already registered.

        Returns:
            LazyUserReadSchema: The created user data.
        """
        existing = await self.user_repos.find_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = SecurityUtils.hash_password(user_create.password)
        user_model = User(
            **user_create.model_dump(exclude=["password"]), password=hashed_pw
        )
        created = await self.user_repos.create(user_model)
        return LazyUserReadSchema.model_validate(created)

    async def update_user(
        self, user_id: str, user_update: UserUpdateSchema
    ) -> LazyUserReadSchema:
        """Update an existing user.

        Args:
            user_id (str): The ID of the user to update.
            user_update (UserUpdateSchema): The user data to update.

        Raises:
            HTTPException: 404 Not Found if the user does not exist.
            HTTPException: 400 Bad Request if the email is already registered.
            HTTPException: 500 Internal Server Error if the update fails.

        Returns:
            LazyUserReadSchema: The updated user data.
        """
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Protection : Seul un superadmin peut modifier un superadmin
        if user.is_superuser():
            # (Vérifier si le requester est superadmin ici si l'info était dispo)
            pass

        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.user_repos.find_by_email(update_data["email"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        if "password" in update_data:
            update_data["password"] = SecurityUtils.hash_password(
                update_data.pop("password")
            )

        for key, value in update_data.items():
            setattr(user, key, value)
        updated = await self.user_repos.update(user)
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

        for key, value in update_data.items():
            setattr(user, key, value)

        updated = await self.user_repos.update(user)
        return UserReadSchema.model_validate(updated)

    async def delete_user(self, user_id: str) -> None:
        """Delete a user by its ID."""
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Protection : Empêcher la suppression d'un superadmin
        if user.is_superuser():
            raise HTTPException(
                status_code=403, detail="Superadmin user cannot be deleted."
            )

        await self.user_repos.delete(user)

    async def add_roles_to_user(
        self, user_id_to_update: str, roles_to_add: List[str]
    ) -> UserReadSchema:
        """Assigns new roles to an existing user."""
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=user_id_to_update)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User '{user_id_to_update}' not found."
            )

        # Protection : Seul un superadmin peut modifier un superadmin
        # (Cette vérification suppose que le middleware a déjà validé l'appelant s'il n'est pas superadmin)
        if user.is_superuser():
            # Ici on pourrait ajouter une vérification du current_user si on l'avait
            pass

        # Valider si toutes les rôles à ajouter existent
        existing_roles = await self.role_repos.find_many_by_ids(ids=roles_to_add)
        existing_role_ids = {str(r.id) for r in existing_roles}

        # Protection : Empêcher l'ajout du rôle superadmin par ID
        if any(r.name == "superadmin" for r in existing_roles):
            raise HTTPException(
                status_code=400, detail="Superadmin role cannot be added."
            )

        invalid_roles = [
            role_id for role_id in roles_to_add if role_id not in existing_role_ids
        ]
        if invalid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Roles not found: {', '.join(invalid_roles)}.",
            )

        # Ajouter les rôles à la relation
        for role in existing_roles:
            if role not in user.roles:
                user.roles.append(role)

        # Mettre à jour l'utilisateur
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update user roles.")

        user = await self.user_repos.find_by_id(id=user_id_to_update)
        return UserReadSchema.model_validate(user)

    async def remove_roles_from_user(
        self, user_id: str, roles_to_remove: List[str]
    ) -> UserReadSchema:
        """Removes specified roles from an existing user."""
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

        # Protection : Vérifier si on essaie de retirer le rôle superadmin
        existing_roles_to_remove = await self.role_repos.find_many_by_ids(
            ids=roles_to_remove
        )
        is_removing_superadmin = any(
            r.name == "superadmin" for r in existing_roles_to_remove
        )

        if is_removing_superadmin:
            # Vérifier si c'est le dernier superadmin
            superadmins = await self.user_repos.list_users(
                role_name="superadmin", all=True
            )
            if len(superadmins) <= 1 and any(
                r.name == "superadmin" for r in user.roles
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot remove the superadmin role from the last superadmin.",
                )

        # Retirer les rôles de la relation
        user_role_ids = {str(r.id) for r in user.roles}
        for role_id in roles_to_remove:
            if role_id in user_role_ids:
                user.roles.remove(next(r for r in user.roles if str(r.id) == role_id))

        # Mettre à jour l'utilisateur
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update user roles.")

        user = await self.user_repos.find_by_id(id=user_id)
        return UserReadSchema.model_validate(user)

    async def add_permissions_to_user(
        self, user_id: str, permissions_to_add: List[str]
    ) -> UserReadSchema:
        """Assigns new permissions to an existing user."""
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

        # Protection : Seul un superadmin peut modifier un superadmin
        if user.is_superuser():
            # (Vérifier si le requester est superadmin ici)
            pass

        # Valider si toutes les permissions à ajouter existent
        existing_permissions = await self.permission_repos.find_many_by_ids(
            ids=permissions_to_add
        )
        existing_permission_ids = {str(p.id) for p in existing_permissions}

        # Protection : Empêcher l'ajout de permissions critiques si nécessaire
        # (Pour l'instant, on se base sur le fait que l'utilisateur a déjà 'superadmin' string check,
        # je vais le garder mais en vérifiant les objets réels)
        # if any("superadmin" in p.code for p in existing_permissions): ...

        invalid_permissions = [
            perm_id
            for perm_id in permissions_to_add
            if perm_id not in existing_permission_ids
        ]
        if invalid_permissions:
            raise HTTPException(
                status_code=400,
                detail=f"Permissions not found: {', '.join(invalid_permissions)}.",
            )

        # Ajouter les permissions à la relation
        for permission in existing_permissions:
            if permission not in user.permissions:
                user.permissions.append(permission)

        # Mettre à jour l'utilisateur
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(
                status_code=500, detail="Failed to update user permissions."
            )

        user = await self.user_repos.find_by_id(id=user_id)
        return UserReadSchema.model_validate(user)

    async def remove_permissions_from_user(
        self, user_id: str, permissions_to_remove: List[str]
    ) -> UserReadSchema:
        """Removes specified permissions from an existing user."""
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

        # Protection : Seul un superadmin peut modifier un superadmin
        if user.is_superuser():
            pass

        # Retirer les permissions de la relation
        user_permission_ids = {str(p.id) for p in user.permissions}
        for permission_id in permissions_to_remove:
            if permission_id in user_permission_ids:
                user.permissions.remove(
                    next(p for p in user.permissions if str(p.id) == permission_id)
                )

        # Mettre à jour l'utilisateur
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(
                status_code=500, detail="Failed to update user permissions."
            )

        user = await self.user_repos.find_by_id(id=user_id)
        return UserReadSchema.model_validate(user)

    """async def get_all_roles(self, user: User) -> set[str]:
        # 1. Roles directes
        roles = set(user.roles)

        # 2. Roles hérités
        seen = set()
        to_visit = list(user.roles)

        while to_visit:
            role_name = to_visit.pop()
            if role_name in seen:
                continue
            seen.add(role_name)

            role = await self.role_repos.find_by_name(role_name)
            if not role:
                continue

            roles.update(role.inherited_roles)
            to_visit.extend(role.inherited_roles)

        return roles
        

    async def has_role(self, user: User, role_name: str) -> bool:
        return role_name in user.roles"""

    async def ensure_role(self, user: User, role_name: str) -> bool:
        if not user.has_role(role_name):
            raise HTTPException(status_code=403, detail="Unauthorized")
        return True

    """async def get_all_permissions(self, user: User) -> set[str]:
        # 1. Permissions directes
        perms = set(user.permissions)

        # 2. Permissions des rôles + hérités
        seen = set()
        to_visit = list(user.roles)

        while to_visit:
            role_name = to_visit.pop()
            if role_name in seen:
                continue
            seen.add(role_name)

            role = await self.role_repos.find_by_name(role_name)
            if not role:
                continue

            perms.update(role.permissions)
            #to_visit.extend(role.inherited_roles)

        return perms


    async def has_permission(self, user: User, permission_code: str) -> bool:
        all_permissions = await self.get_all_permissions(user)
        return permission_code in all_permissions"""

    async def ensure_permission(self, user: User, permission_code: str) -> bool:
        if not user.has_permission(permission_code):
            raise HTTPException(status_code=403, detail="Permission denied")
        return True
