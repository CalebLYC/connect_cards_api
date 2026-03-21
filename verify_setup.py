import asyncio
import sys
import os
import traceback

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

from app.services.setup_service import SetupService
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.db.db_client import PostgresClient
from app.core.config import Settings


async def run_setup():
    settings = Settings()
    # Disable echo to reduce noise
    postgres = PostgresClient(uri=settings.database_uri)
    postgres.engine.echo = False

    try:
        async for db in postgres.get_session():
            try:
                user_repos = UserRepository(db)
                role_repos = RoleRepository(db)
                permission_repos = PermissionRepository(db)
                setup_service = SetupService(
                    user_repos, role_repos, permission_repos, settings
                )

                result = await setup_service.setup_roles_and_permissions()
                print(f"Setup Result: {result}")

                # Verify roles
                for role_name in ["admin", "organization_admin"]:
                    role = await role_repos.find_by_name(role_name)
                    if role:
                        print(
                            f"\nRole '{role_name}' has {len(role.permissions)} permissions."
                        )

                        # Check for specific read permissions that were previously excluded
                        critical_resources = [
                            "webhook",
                            "card_assignment_history",
                            "event",
                            "identity_project_permission",
                        ]
                        for res in critical_resources:
                            perm_code = f"{res}:read"
                            has_perm = any(
                                p.code == perm_code for p in role.permissions
                            )
                            has_manage = any(
                                p.code == f"{res}:manage" for p in role.permissions
                            )
                            print(
                                f"  {perm_code}: {'YES' if has_perm else 'NO'}, {res}:manage: {'YES' if has_manage else 'NO'}"
                            )

                await db.commit()  # Final commit in case something wasn't
            except Exception:
                traceback.print_exc()
                await db.rollback()
            break
    finally:
        await postgres.close()


if __name__ == "__main__":
    asyncio.run(run_setup())
