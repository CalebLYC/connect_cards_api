from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.providers.providers import get_db
from app.db.repositories.permission_repository import PermissionRepository


def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db=db)


def get_access_token_repository(db: AsyncSession = Depends(get_db)):
    return AccessTokenRepository(db=db)


def get_role_repository(db: AsyncSession = Depends(get_db)):
    return RoleRepository(db=db)


def get_permission_repository(db: AsyncSession = Depends(get_db)):
    return PermissionRepository(db=db)
