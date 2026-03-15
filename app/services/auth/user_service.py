from typing import Optional, List
from app.core.security import SecurityUtils
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user_schema import LazyUserReadSchema, UserCreateSchema, UserUpdateSchema, UserReadSchema
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
        """Delete a user by its ID.

        Args:
            user_id (str): The ID of the user to delete.

        Raises:
            HTTPException: 404 If the user is not found.
        """
        user = await self.user_repos.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await self.user_repos.delete(user)
        
        
    async def add_roles_to_user(
        self, role_id: str, roles_to_add: List[str]
    ) -> UserReadSchema:
        """
        Assigns new roles to an existing user.

        Args:
            role_id (str): The id of the role to update.
            roles_to_add (List[str]): A list of role codes to add.

        Returns:
            UserReadSchema: The updated user.

        Raises:
            HTTPException: If the user is not found or any role is invalid.
        """
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=role_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{role_id}' not found.")

        # Valider si toutes les rôles à ajouter existent
        existing_roles = await self.role_repos.find_many_by_ids(ids=roles_to_add)
        #print(f"Existing roles: {list(existing_roles)}")
        existing_role_ids = {str(r.id) for r in existing_roles}
        #print(f"Existing role ids: {list(existing_role_ids)}")
        
        invalid_roles = [role_id for role_id in roles_to_add if role_id not in existing_role_ids]
        if invalid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Roles not found: {', '.join(invalid_roles)}. Please create them first.",
            )

        # Ajouter les rôles à la relation
        for role in existing_roles:
            if role not in user.roles:
                user.roles.append(role)

        # Mettre à jour l'utilisateur dans la base de données
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update user roles.")
        user = await self.user_repos.find_by_id(id=role_id)
        # Retourner l'utilisateur mis à jour
        return UserReadSchema.model_validate(user)
    
    
    async def remove_roles_from_user(
        self, user_id: str, roles_to_remove: List[str]
    ) -> UserReadSchema:
        """
        Removes specified roles from an existing user.

        Args:
            user_id (str): The ID of the user to update.
            roles_to_remove (List[str]): A list of role codes to remove.

        Returns:
            UserReadSchema: The updated user.

        Raises:
            HTTPException: If the user is not found or any role is invalid.
        """
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
        
        # Retirer les rôles de la relation
        user_role_ids = {str(r.id) for r in user.roles}
        for role_id in roles_to_remove:
            if role_id in user_role_ids:
                user.roles.remove(next(r for r in user.roles if str(r.id) == role_id))

        # Mettre à jour l'utilisateur dans la base de données
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update user roles.")

        # Retourner l'utilisateur mis à jour
        return UserReadSchema.model_validate(user)


    async def add_permissions_to_user(
        self, role_id: str, permissions_to_add: List[str]
    ) -> UserReadSchema:
        """
        Assigns new permissions to an existing user.

        Args:
            role_id (str): The id of the role to update.
            permissions_to_add (List[str]): A list of permission codes to add.

        Returns:
            UserReadSchema: The updated user.

        Raises:
            HTTPException: If the user is not found or any permission is invalid.
        """
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=role_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{role_id}' not found.")

        # Valider si toutes les permissions à ajouter existent
        existing_permissions = await self.permission_repos.find_many_by_ids(ids=permissions_to_add)
        #print(f"Existing permissions: {list(existing_permissions)}")
        existing_permission_ids = {str(p.id) for p in existing_permissions}
        #print(f"Existing permission ids: {list(existing_permission_ids)}")
        
        invalid_permissions = [perm_id for perm_id in permissions_to_add if perm_id not in existing_permission_ids]
        if invalid_permissions:
            raise HTTPException(
                status_code=400,
                detail=f"Permissions not found: {', '.join(invalid_permissions)}. Please create them first.",
            )

        # Ajouter les permissions à la relation
        for permission in existing_permissions:
            if permission not in user.permissions:
                user.permissions.append(permission)

        # Mettre à jour l'utilisateur dans la base de données
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update user permissions.")

        # Retourner l'utilisateur mis à jour
        return UserReadSchema.model_validate(user)


    async def remove_permissions_from_user(
        self, user_id: str, permissions_to_remove: List[str]
    ) -> UserReadSchema:
        """
        Removes specified permissions from an existing user.

        Args:
            user_id (str): The ID of the user to update.
            permissions_to_remove (List[str]): A list of permission codes to remove.

        Returns:
            UserReadSchema: The updated user.

        Raises:
            HTTPException: If the user is not found or any permission is invalid.
        """
        # Récupérer l'utilisateur
        user = await self.user_repos.find_by_id(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
        
        # Retirer les permissions de la relation
        user_permission_ids = {str(p.id) for p in user.permissions}
        for permission_id in permissions_to_remove:
            if permission_id in user_permission_ids:
                user.permissions.remove(next(p for p in user.permissions if str(p.id) == permission_id))

        # Mettre à jour l'utilisateur dans la base de données
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update user permissions.")

        # Retourner l'utilisateur mis à jour
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
        db_role = await self.role_repos.find_by_name(name=role_name)
        if not db_role:
            raise HTTPException(status_code=500, detail="Unkown role")
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

    async def ensure_permission(
        self, user: User, permission_code: str
    ) -> bool:
        db_permission = await self.permission_repos.find_by_code(code=permission_code)
        if not db_permission:
            raise HTTPException(status_code=500, detail="Unkown permission")
        if not user.has_permission(permission_code):
            raise HTTPException(status_code=403, detail="Permission denied")
        return True
