from starlette.exceptions import HTTPException
import datetime

from app.core.config import Settings
from app.core.security import SecurityUtils

# from app.models.permission import Permission
from app.models.permission import Permission
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
            superadmin_role = await self.role_repos.create(
                Role(
                    name="superadmin",
                    description="Superadmin role with all permissions",
                )
            )

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
            raise HTTPException(
                status_code=500, detail="Failed to create superadmin user."
            )

        # Update the created user to have superadmin role and permissions
        user = await self.user_repos.find_by_id(id=db_user.id)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to upgrade privileges.")
        user.is_verified = True
        user.is_active = True
        user.roles.append(superadmin_role)
        # user.permissions.append(superadmin_permission)
        await self.user_repos.update(user)

        return {"message": "Superadmin user setup successfully."}

    async def setup_roles_and_permissions(self) -> dict:
        """Set up roles and permissions.
        Args:
            None
        Returns:
            dict: Success message.
        """
        # Create default roles if they don't exist
        roles_data = [
            {
                "name": "superadmin",
                "description": "Superadmin role with all permissions",
            },
            {"name": "admin", "description": "Admin role with elevated permissions"},
            {
                "name": "organization_admin",
                "description": "Organization Admin role with permissions for their organization",
            },
            {
                "name": "user",
                "description": "Regular user role with limited permissions",
            },
        ]

        db_roles = {}
        for role_item in roles_data:
            role = await self.role_repos.find_by_name(role_item["name"])
            if not role:
                role = await self.role_repos.create(Role(**role_item))
            db_roles[role_item["name"]] = role

        # Define resources and actions for permissions
        resources = [
            "role",
            "permission",
            "user",
            "organization",
            "project",
            "card",
            "reader",
            "identity",
            "membership",
            "event",
            "webhook",
            "card_assignment_history",
            "identity_project_permission",
        ]
        actions = ["manage", "read", "create", "update", "delete"]

        permissions_data = []
        for resource in resources:
            for action in actions:
                permissions_data.append(
                    {
                        "code": f"{resource}:{action}",
                        "description": f"Permission to {action} {resource.replace('_', ' ')}s",
                    }
                )

        # Add special permissions
        special_permissions = [
            {
                "code": "organization:own",
                "description": "Permission to manage own organization",
            },
            {"code": "admin:manage", "description": "Permission to manage admin users"},
        ]
        permissions_data.extend(special_permissions)

        all_permissions = []
        for permission_item in permissions_data:
            permission = await self.permission_repos.find_by_code(
                permission_item["code"]
            )
            if not permission:
                permission = await self.permission_repos.create(
                    Permission(**permission_item)
                )
            all_permissions.append(permission)

        # Assign permissions to admin and organization_admin roles with specific exclusions
        # admin excludes: webhook:*, admin:manage, card_assignment_history:*, event:*, identity_project_permission:*
        admin_excludes = [
            "webhook",
            "admin:manage",
            "card_assignment_history",
            "event",
            "identity_project_permission",
        ]

        # organization_admin excludes: admin:manage, card_assignment_history:*, event:*
        org_admin_excludes = ["admin:manage", "card_assignment_history", "event"]

        for role_name in ["admin", "organization_admin"]:
            role = db_roles.get(role_name)
            if role:
                role.permissions = []
                excludes = (
                    admin_excludes if role_name == "admin" else org_admin_excludes
                )

                for perm in all_permissions:
                    is_excluded = False
                    for ex in excludes:
                        # If the exclusion is a resource name (like 'webhook'), exclude its actions except 'read'
                        if perm.code == ex or perm.code.startswith(f"{ex}:"):
                            if not perm.code.endswith(":read"):
                                is_excluded = True
                                break

                    if not is_excluded:
                        role.permissions.append(perm)

                await self.role_repos.update(role)

        return {"message": "Roles and permissions setup successfully."}

    async def webhook_test(self) -> dict:
        """Test webhook functionality.
        Args:
            None
        Returns:
            dict: Success message.
        """
        print("Webhook test successful at " + datetime.datetime.now().isoformat())
        return {
            "message": "Webhook test successful at "
            + datetime.datetime.now().isoformat()
        }
