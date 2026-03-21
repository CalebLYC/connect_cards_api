from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.access_token import AccessToken
from app.models.user import User
from app.models.role import Role


class AccessTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: str):
        stmt = (
            select(AccessToken)
            .options(selectinload(AccessToken.user))
            .where(AccessToken.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_token(self, token: str) -> Optional[AccessToken]:
        stmt = (
            select(AccessToken)
            .options(
                selectinload(AccessToken.user)
                .selectinload(User.roles)
                .selectinload(Role.permissions),
                selectinload(AccessToken.user).selectinload(User.permissions),
                selectinload(AccessToken.user).selectinload(User.organization),
            )
            .where(AccessToken.token == token)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_access_tokens(
        self,
        skip: int = 0,
        limit: Optional[int] = 100,
        all: bool = False,
    ) -> List[AccessToken]:

        stmt = select(AccessToken)

        if not all:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, access_token: AccessToken) -> AccessToken:
        self.db.add(access_token)
        await self.db.commit()
        await self.db.refresh(access_token)
        return access_token

    async def update(self, access_token: AccessToken) -> AccessToken:
        await self.db.commit()
        await self.db.refresh(access_token)
        return access_token

    async def delete(self, access_token: AccessToken) -> None:
        await self.db.delete(access_token)
        await self.db.commit()

    async def delete_by_user_id(self, user_id) -> None:
        if isinstance(user_id, str):
            user_uuid = uuid.UUID(user_id)
        else:
            user_uuid = user_id
        stmt = delete(AccessToken).where(AccessToken.user_id == user_uuid)
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(AccessToken)
        await self.db.execute(stmt)
        await self.db.commit()
