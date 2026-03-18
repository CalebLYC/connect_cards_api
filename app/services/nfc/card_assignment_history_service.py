from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.card_assignment_history import CardAssignmentHistory
from app.repositories.card_assignment_history_repository import (
    CardAssignmentHistoryRepository,
)
from app.schemas.card_assignment_history_schema import (
    CardAssignmentHistoryReadSchema,
    LazyCardAssignmentHistoryReadSchema,
    CardAssignmentHistoryCreateSchema,
    CardAssignmentHistoryUpdateSchema,
)


class CardAssignmentHistoryService:
    def __init__(self, history_repos: CardAssignmentHistoryRepository):
        self.history_repos = history_repos

    async def get_history(
        self, history_id: str, eager: bool = True
    ) -> Optional[CardAssignmentHistoryReadSchema]:
        if eager:
            history = await self.history_repos.find_by_id_eager(history_id)
        else:
            history = await self.history_repos.find_by_id(history_id)

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="History record not found"
            )
        return CardAssignmentHistoryReadSchema.model_validate(history)

    async def list_histories(
        self,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        eager: bool = False,
    ) -> List[CardAssignmentHistoryReadSchema]:
        if eager:
            histories = await self.history_repos.find_many_eager(filters, skip, limit)
        else:
            histories = await self.history_repos.find_many(filters, skip, limit)
        return [CardAssignmentHistoryReadSchema.model_validate(h) for h in histories]

    async def create_history(
        self, history_create: CardAssignmentHistoryCreateSchema
    ) -> LazyCardAssignmentHistoryReadSchema:
        try:
            history_model = CardAssignmentHistory(**history_create.model_dump())
            created = await self.history_repos.create(history_model)
            return LazyCardAssignmentHistoryReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown card or identity id",
            )

    async def update_history(
        self, history_id: str, history_update: CardAssignmentHistoryUpdateSchema
    ) -> LazyCardAssignmentHistoryReadSchema:
        try:
            history = await self.history_repos.find_by_id(history_id)
            if not history:
                raise HTTPException(status_code=404, detail="History record not found")

            update_data = history_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(history, key, value)

            updated = await self.history_repos.update(history)
            return LazyCardAssignmentHistoryReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown card or identity id",
            )

    async def delete_history(self, history_id: str) -> None:
        history = await self.history_repos.find_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="History record not found")
        await self.history_repos.delete(history)

    async def delete_all_histories(self) -> None:
        await self.history_repos.delete_all()
