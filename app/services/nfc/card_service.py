import secrets
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.card import Card
from app.models.card_assignment_history import CardAssignmentHistory
from app.repositories.card_repository import CardRepository
from app.schemas.card_schema import (
    CardReadSchema,
    LazyCardReadSchema,
    CardCreateSchema,
    CardUpdateSchema,
)
from app.schemas.identity_schema import LazyIdentityReadSchema
from app.exceptions.card_exceptions import (
    CardNotFoundException,
    UnauthorizedAccessException,
    IdentityNotAssignedException,
    ProjectNotFoundException,
    CardAlreadyActiveException,
    InvalidActivationCodeException,
    ActivationCodeExpiredException,
    CardNotActiveException,
)
from app.schemas.nfc_schema import (
    ScanCardResponse,
    CardActivationRequest,
    CardActivationResponse,
)
from app.core.config import Settings
import datetime


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

    async def scan_card(self, card_uid: str, project_id: Any) -> ScanCardResponse:
        try:
            result = await self.card_repos.get_card_with_access_details(
                card_uid, project_id
            )

            identity = result["identity"]
            membership = result["membership"]

            # Extract Permissions (Roles from membership)
            permissions_list = (
                membership.roles if membership and membership.roles else []
            )

            return ScanCardResponse(
                authorized=True,
                user=LazyIdentityReadSchema.model_validate(identity),
                permissions=permissions_list,
            )

        except CardNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except ProjectNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except IdentityNotAssignedException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except CardInactiveException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except UnauthorizedAccessException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except CardAlreadyActiveException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        except InvalidActivationCodeException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        except ActivationCodeExpiredException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )

    async def activate_card(
        self, request: CardActivationRequest, settings: Settings
    ) -> CardActivationResponse:
        """
        Activates a card by linking it to an identity using an activation code.
        Atomicity is ensured by SQLAlchemy transaction management.
        """
        try:
            card = await self.card_repos.find_by_uid(request.card_uid)
            if not card:
                raise CardNotFoundException(request.card_uid)

            """identity = await self.identity_repos.find_by_id(request.identity_id)
            if not identity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Identity not found",
                )
            if card.issuer_organization_id != identity.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Card does not belong to the authenticated organization",
                )"""

            # 1. Check if already active
            if card.status == "active":
                raise CardAlreadyActiveException(request.card_uid)

            # 2. Validate Code
            if card.activation_code != request.activation_code:
                raise InvalidActivationCodeException(request.card_uid)

            # 3. Check Expiry
            if card.created_at:
                expiry_delta = datetime.timedelta(
                    minutes=settings.card_activation_code_expiry_minutes
                )
                if (
                    datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                    > card.created_at + expiry_delta
                ):
                    raise ActivationCodeExpiredException(request.card_uid)

            # 4. Atomic Update
            # Add history record
            history = CardAssignmentHistory(
                card_id=card.id, identity_id=request.identity_id
            )
            self.card_repos.db.add(history)

            card.identity_id = request.identity_id
            card.status = "active"
            card.activation_code = None

            updated = await self.card_repos.update(card)

            return CardActivationResponse(
                success=True, card=LazyCardReadSchema.model_validate(updated)
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'identifiant d'identité fourni n'existe pas.",
            )
        except CardNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except CardAlreadyActiveException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        except InvalidActivationCodeException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        except ActivationCodeExpiredException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )

    async def revoke_card(self, card_uid: str) -> CardActivationResponse:
        """
        Revokes a card by unlinking the identity and closing the history record.
        Resets card to pending with a new activation code.
        """
        try:
            card = await self.card_repos.find_by_uid(card_uid)
            if not card:
                raise CardNotFoundException(card_uid)

            if card.status != "active" or not card.identity_id:
                raise CardNotActiveException(card_uid)

            # 1. Close history record
            history = await self.card_repos.get_active_assignment(card.id)
            if history:
                history.unassigned_at = datetime.datetime.now(
                    datetime.timezone.utc
                ).replace(tzinfo=None)
                self.card_repos.db.add(history)

            # 2. Reset Card
            card.identity_id = None
            card.status = "pending"
            card.activation_code = self.generate_activation_code()

            updated = await self.card_repos.update(card)

            return CardActivationResponse(
                success=True, card=LazyCardReadSchema.model_validate(updated)
            )
        except CardNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except CardNotActiveException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during revocation: {str(e)}",
            )

    @staticmethod
    def generate_activation_code() -> str:
        return secrets.token_urlsafe(16)
