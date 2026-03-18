from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.models.card import Card


class CardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: Any) -> Optional[Card]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(Card).where(Card.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_eager(self, id: Any) -> Optional[Card]:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            select(Card)
            .options(
                selectinload(Card.identity),
                selectinload(Card.issuer_organization),
                # selectinload(Card.assignment_history),
                # selectinload(Card.events),
            )
            .where(Card.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_uid(self, uid: str) -> Optional[Card]:
        stmt = select(Card).where(Card.uid == uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_many(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Card]:
        stmt = select(Card)
        if filters:
            for key, value in filters.items():
                if hasattr(Card, key):
                    stmt = stmt.where(getattr(Card, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_many_eager(
        self, filters: dict = None, skip: int = 0, limit: int = 100
    ) -> List[Card]:
        stmt = select(Card).options(
            selectinload(Card.identity),
            selectinload(Card.issuer_organization),
            # selectinload(Card.assignment_history),
            # selectinload(Card.events),
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Card, key):
                    stmt = stmt.where(getattr(Card, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Card]:
        stmt = select(Card).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_eager(self, skip: int = 0, limit: int = 100) -> List[Card]:
        stmt = (
            select(Card)
            .options(
                selectinload(Card.identity),
                selectinload(Card.issuer_organization),
                # selectinload(Card.assignment_history),
                # selectinload(Card.events),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, card: Card) -> Card:
        self.db.add(card)
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def update(self, card: Card) -> Card:
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def delete(self, card: Card) -> None:
        await self.db.delete(card)
        await self.db.commit()

    async def delete_all(self) -> None:
        stmt = delete(Card)
        await self.db.execute(stmt)
        await self.db.commit()
