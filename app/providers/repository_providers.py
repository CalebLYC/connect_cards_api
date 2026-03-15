from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.identity_repository import IdentityRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.providers.providers import get_db
from app.repositories.permission_repository import PermissionRepository


def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db=db)


def get_identity_repository(db: AsyncSession = Depends(get_db)):
    return IdentityRepository(db=db)


def get_access_token_repository(db: AsyncSession = Depends(get_db)):
    return AccessTokenRepository(db=db)


def get_role_repository(db: AsyncSession = Depends(get_db)):
    return RoleRepository(db=db)


def get_permission_repository(db: AsyncSession = Depends(get_db)):
    return PermissionRepository(db=db)
