from fastapi import Depends
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.identity_repository import IdentityRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.repositories.permission_repository import PermissionRepository

from app.services.auth.identity_service import IdentityService
from app.services.auth.permission_service import PermissionService
from app.providers.repository_providers import (
    get_access_token_repository,
    get_role_repository,
    get_user_repository,
    get_permission_repository,
    get_identity_repository,
)
from app.services.auth.auth_service import AuthService
from app.services.auth.role_service import RoleService
from app.services.auth.user_service import UserService


def get_user_service(
    user_repos: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Provides user service

    Args:
        user_repos (UserRepository, optional): _description_. Defaults to Depends(get_user_repository).
        role_repos (RoleRepository, optional): _description_. Defaults to Depends(get_role_repository).
        permission_repos (PermissionRepository, optional): _description_. Defaults to Depends(get_permission_repository).

    Returns:
        UserService: _description_
    """
    return UserService(user_repos=user_repos)


def get_identity_service(
    identity_repos: IdentityRepository = Depends(get_identity_repository),
) -> IdentityService:
    return IdentityService(identity_repos=identity_repos)


def get_auth_service(
    user_repos: UserRepository = Depends(get_user_repository),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> UserService:
    return AuthService(user_repos=user_repos, access_token_repos=access_token_repos)


def get_role_service(
    role_repos: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    return RoleService(role_repos=role_repos)

# Ajouter à la fin du fichier existant
def get_permission_service(
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> PermissionService:
    return PermissionService(permission_repos=permission_repos)