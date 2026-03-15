from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def find_by_id(self, id: str):
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .options(selectinload(User.permissions))
            .where(User.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def find_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            #.options(selectinload(User.roles))
            #.options(selectinload(User.permissions))
            .where(User.email == email)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def find_by_phone_number(self, phone_number: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            #.options(selectinload(User.permissions))
            .where(User.phone_number == phone_number)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def list_users(
        self,
        skip: int = 0,
        limit: Optional[int] = 100,
        all: bool = False,
    ) -> List[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .options(selectinload(User.permissions))
        )
        
        if not all:
            stmt = stmt.offset(skip).limit(limit)
            
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def update(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
