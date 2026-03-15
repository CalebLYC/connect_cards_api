from starlette.exceptions import HTTPException

from app.core.config import Settings
from app.core.security import SecurityUtils
#from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.providers.providers import get_settings
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from fastapi import Depends


class SetupService:
    def __init__(
        self,
        user_repos: UserRepository,
        role_repos: RoleRepository,
        permission_repos: PermissionRepository,
        settings: Settings = Depends(get_settings),
    ):
        self.user_repos = user_repos
        self.role_repos = role_repos
        self.permission_repos = permission_repos
        self.settings = settings


    async def setup_superadmin(self) -> dict:
        """Set up the superadmin user.
            Args:
                None
            Returns:
                dict: Success message.
        """
        superadmin_email = self.settings.admin_email or "superadmin@example.com"
        superadmin_password = self.settings.admin_password
        if not superadmin_password:
            raise ValueError("Admin password must be set.")
        
        # Check if superadmin user already exists
        existing = await self.user_repos.find_by_email(superadmin_email)
        if existing:
            return {"message": "Superadmin user setup successfully."}
        
        # Create superadmin role if it doesn't exist
        superadmin_role = await self.role_repos.find_by_name("superadmin")
        if not superadmin_role:
            superadmin_role = await self.role_repos.create(Role(name="superadmin", description="Superadmin role with all permissions"))

        """# Create superadmin permissions if they don't exist
        superadmin_permission = await self.permission_repos.find_by_code("superadmin")
        if not superadmin_permission:
            superadmin_permission = await self.permission_repos.create(Permission(code="superadmin", description="Superadmin permission with all access"))"""

        # Create superadmin user
        user_create = User(
            email=superadmin_email,
            password=SecurityUtils.hash_password(superadmin_password),
            full_name="Super Admin",
        )
        db_user = await self.user_repos.create(user=user_create)
        if not db_user:
            raise HTTPException(status_code=500, detail="Failed to create superadmin user.")
        
        # Update the created user to have superadmin role and permissions
        user = await self.user_repos.find_by_id(id= db_user.id)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to upgrade privileges.")
        user.is_verified = True
        user.is_active = True
        user.roles.append(superadmin_role)
        #user.permissions.append(superadmin_permission)
        await self.user_repos.update(user)
        
        return {"message": "Superadmin user setup successfully."}