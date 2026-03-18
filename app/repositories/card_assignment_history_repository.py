from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.card_assignment_history import CardAssignmentHistory


class CardAssignmentHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[CardAssignmentHistory]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(CardAssignmentHistory).where(CardAssignmentHistory.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[CardAssignmentHistory]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(CardAssignmentHistory)
            .options(
                selectinload(CardAssignmentHistory.card),
                selectinload(CardAssignmentHistory.identity),
            )
            .where(CardAssignmentHistory.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[CardAssignmentHistory]:
        stmt = select(CardAssignmentHistory)
        if filters:
            for key, value in filters.items():
                if hasattr(CardAssignmentHistory, key):
                    stmt = stmt.where(getattr(CardAssignmentHistory, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[CardAssignmentHistory]:
        stmt = (
            select(CardAssignmentHistory)
            .options(
                selectinload(CardAssignmentHistory.card),
                selectinload(CardAssignmentHistory.identity),
            )
        )
        if filters:
            for key, value in filters.items():
                if hasattr(CardAssignmentHistory, key):
                    stmt = stmt.where(getattr(CardAssignmentHistory, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(self, skip: int = 0, limit: int = 100) -> List[CardAssignmentHistory]:
        stmt = select(CardAssignmentHistory).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(self, skip: int = 0, limit: int = 100) -> List[CardAssignmentHistory]:
        stmt = (
            select(CardAssignmentHistory)
            .options(
                selectinload(CardAssignmentHistory.card),
                selectinload(CardAssignmentHistory.identity),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, history: CardAssignmentHistory) -> CardAssignmentHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def create_many(self, histories: List[CardAssignmentHistory]) -> List[CardAssignmentHistory]:
        self.db.add_all(histories)
        await self.db.commit()
        for history in histories:
            await self.db.refresh(history)
        return histories

    async def update(self, history: CardAssignmentHistory) -> CardAssignmentHistory:
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def delete(self, history: CardAssignmentHistory) -> None:
        await self.db.delete(history)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(CardAssignmentHistory)
        await self.db.execute(stmt)
        await self.db.commit()
