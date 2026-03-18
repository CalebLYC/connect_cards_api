import secrets
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.card import Card
from app.repositories.card_repository import CardRepository
from app.schemas.card_schema import (
    CardReadSchema,
    LazyCardReadSchema,
    CardCreateSchema,
    CardUpdateSchema,
)


class CardService:
    def __init__(self, card_repos: CardRepository):
        self.card_repos = card_repos

    async def get_card(
        self, card_id: str, eager: bool = True
    ) -> Optional[CardReadSchema]:
        if eager:
            card = await self.card_repos.find_by_id_eager(card_id)
        else:
            card = await self.card_repos.find_by_id(card_id)

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )
        return CardReadSchema.model_validate(card)

    async def get_card_by_uid(self, uid: str) -> CardReadSchema:
        card = await self.card_repos.find_by_uid(uid)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )
        return CardReadSchema.model_validate(card)

    async def list_cards(
        self,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        eager: bool = False,
    ) -> List[CardReadSchema]:
        if eager:
            cards = await self.card_repos.find_many_eager(filters, skip, limit)
        else:
            cards = await self.card_repos.find_many(filters, skip, limit)
        return [CardReadSchema.model_validate(c) for c in cards]

    async def create_card(self, card_create: CardCreateSchema) -> LazyCardReadSchema:
        try:
            db_card = await self.card_repos.find_by_uid(card_create.uid)
            if db_card:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Card with this UID already exists",
                )
            activation_code = self.generate_activation_code()
            card_model = Card(
                **card_create.model_dump(), activation_code=activation_code
            )
            created = await self.card_repos.create(card_model)
            return LazyCardReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity id or issuer organization id",
            )

    async def update_card(
        self, card_id: str, card_update: CardUpdateSchema
    ) -> LazyCardReadSchema:
        try:
            card = await self.card_repos.find_by_id(card_id)
            if not card:
                raise HTTPException(status_code=404, detail="Card not found")

            if card_update.uid:
                db_card = await self.card_repos.find_by_uid(card_update.uid)
                if db_card and db_card.id != card_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Card with this UID already exists",
                    )

            update_data = card_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(card, key, value)

            updated = await self.card_repos.update(card)
            return LazyCardReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity id or issuer organization id",
            )

    async def delete_card(self, card_id: str) -> None:
        card = await self.card_repos.find_by_id(card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        await self.card_repos.delete(card)

    async def delete_all_cards(self) -> None:
        await self.card_repos.delete_all()

    @staticmethod
    def generate_activation_code() -> str:
        return secrets.token_urlsafe(16)
