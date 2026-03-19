from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
import uuid

from app.models.card import Card
from app.models.identity import Identity
from app.models.identity_project_permission import IdentityProjectPermission
from app.models.membership import Membership
from app.models.project import Project
from app.exceptions.card_exceptions import (
    CardNotFoundException,
    UnauthorizedAccessException,
    CardInactiveException,
    IdentityNotAssignedException,
    ProjectNotFoundException,
)


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

    async def get_card_with_access_details(
        self, card_uid: str, project_id: Any
    ) -> dict:
        """
        Optimized single-query method to fetch all data required for card access validation.
        Uses LEFT OUTER JOINs to identify precisely which part of the chain is missing in one trip.
        """
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)

        # Main query to fetch data. LEFT joins ensure we get a row if the Card exists.
        # We include Project in the query to validate its existence simultaneously.
        stmt = (
            select(Card, Identity, IdentityProjectPermission, Membership, Project)
            .outerjoin(Identity, Card.identity_id == Identity.id)
            .outerjoin(Project, Project.id == project_id)
            .outerjoin(
                IdentityProjectPermission,
                (Identity.id == IdentityProjectPermission.identity_id)
                & (IdentityProjectPermission.project_id == Project.id),
            )
            .outerjoin(
                Membership,
                (Identity.id == Membership.identity_id)
                & (Membership.organization_id == Project.organization_id),
            )
            .where(Card.uid == card_uid)
        )

        result = await self.db.execute(stmt)
        row = result.first()

        # 1. Check if Card exists
        if not row:
            raise CardNotFoundException(card_uid)

        card, identity, permission, membership, project = row

        # 2. Check if Identity is assigned to the card
        if not identity:
            raise IdentityNotAssignedException(card_uid)

        # 3. Check if Project exists
        if not project:
            raise ProjectNotFoundException(project_id)

        # 4. Check Card Status
        if card.status != "active":
            raise CardInactiveException(card_uid)

        # 5. Check Permissions
        if not permission or not permission.allowed:
            raise UnauthorizedAccessException(identity.id, project_id)

        return {
            "card": card,
            "identity": identity,
            "permission": permission,
            "membership": membership,
            "project": project,
        }
