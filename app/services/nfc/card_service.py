import secrets
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.card import Card
from app.models.card_assignment_history import CardAssignmentHistory
from app.repositories.card_repository import CardRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.identity_repository import IdentityRepository
from app.repositories.event_repository import EventRepository
from app.services.nfc.identity_service import IdentityService
from app.models.event import Event
from app.models.enums.event_type_enum import EventTypeEnum
from fastapi import BackgroundTasks
from app.schemas.card_schema import (
    CardReadSchema,
    LazyCardReadSchema,
    CardCreateSchema,
    CardUpdateSchema,
)
from app.schemas.identity_schema import LazyIdentityReadSchema
from app.exceptions.card_exceptions import (
    CardNotFoundException,
    CardInactiveException,
    UnauthorizedAccessException,
    IdentityNotAssignedException,
    ProjectNotFoundException,
    CardAlreadyActiveException,
    InvalidActivationCodeException,
    ActivationCodeExpiredException,
    CardNotActiveException,
    MembershipNotFoundException,
    MembershipInactiveException,
)
from app.schemas.nfc_schema import (
    ScanCardResponse,
    CardActivationRequest,
    CardActivationResponse,
)
from app.core.config import Settings
import datetime
from app.services.nfc.webhook_service import WebhookService


class CardService:
    def __init__(
        self,
        card_repos: CardRepository,
        membership_repos: MembershipRepository = None,
        identity_repos: IdentityRepository = None,
        event_repos: EventRepository = None,
        webhook_service: WebhookService = None,
    ):
        self.card_repos = card_repos
        self.membership_repos = membership_repos
        self.identity_repos = identity_repos
        self.event_repos = event_repos
        self.webhook_service = webhook_service

    def _log_event(
        self,
        event_type: EventTypeEnum,
        card_id: Optional[Any] = None,
        reader_id: Optional[Any] = None,
        project_id: Optional[Any] = None,
        metadata_desc: Optional[Dict[str, Any]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        """
        Helper method to log events and trigger webhooks in the background.
        """
        if not self.event_repos:
            return

        async def _save_and_trigger_event():
            event = Event(
                card_id=card_id,
                reader_id=reader_id,
                project_id=project_id,
                event_type=event_type,
                metadata_desc=metadata_desc,
            )
            created_event = await self.event_repos.create(event)

            # Trigger webhooks if service is available
            if self.webhook_service and background_tasks:
                await self.webhook_service.trigger_webhooks(
                    created_event, background_tasks
                )
            elif self.webhook_service:
                # If no background_tasks (e.g. internal call), we still want to trigger
                # but we'd need a separate way to handle the async dispatch if not in a request context.
                # For now, we assume background_tasks is preferred.
                import asyncio

                await self.webhook_service.trigger_webhooks(
                    created_event, background_tasks
                )  # This might still need bg tasks

        if background_tasks:
            background_tasks.add_task(_save_and_trigger_event)
        else:
            import asyncio

            asyncio.create_task(_save_and_trigger_event())

    async def _verify_membership(
        self, identity_id: uuid.UUID, organization_id: uuid.UUID
    ):
        """
        Private helper to verify that an identity has an active membership
        in the organization.
        """
        if not self.membership_repos:
            return  # Skip if repository not provided (e.g. in minimal tests)

        membership = await self.membership_repos.find_by_identity_and_organization(
            identity_id, organization_id
        )
        if not membership:
            raise MembershipNotFoundException(identity_id, organization_id)
        if membership.status != "active":
            raise MembershipInactiveException(identity_id, organization_id)

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

    async def create_card(
        self,
        card_create: CardCreateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyCardReadSchema:
        try:
            db_card = await self.card_repos.find_by_uid(card_create.uid)
            if db_card:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "create_card",
                        "reason": "Card with this UID already exists",
                        "uid": card_create.uid,
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Card with this UID already exists",
                )
            if card_create.identity_id and card_create.issuer_organization_id:
                await self._verify_membership(
                    card_create.identity_id, card_create.issuer_organization_id
                )

            activation_code = self.generate_activation_code()
            card_model = Card(
                **card_create.model_dump(), activation_code=activation_code
            )
            created = await self.card_repos.create(card_model)

            # Log event
            self._log_event(
                event_type=EventTypeEnum.CARD_ISSUED,
                card_id=created.id,
                metadata_desc={
                    "uid": created.uid,
                    "action": "create_card",
                    "identity_id": (
                        str(created.identity_id) if created.identity_id else None
                    ),
                },
                background_tasks=background_tasks,
            )

            return LazyCardReadSchema.model_validate(created)
        except IntegrityError as e:
            print(e)
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "create_card",
                    "reason": "Integrity error. Unknown identity or organization id",
                    "uid": card_create.uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity id or issuer organization id",
            )
        except MembershipNotFoundException as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "create_card",
                    "reason": e.message,
                    "uid": card_create.uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except MembershipInactiveException as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "create_card",
                    "reason": e.message,
                    "uid": card_create.uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)

    async def update_card(
        self,
        card_id: str,
        card_update: CardUpdateSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> LazyCardReadSchema:
        try:
            card = await self.card_repos.find_by_id(card_id)
            if not card:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "update_card",
                        "reason": "Card not found",
                        "card_id": str(card_id),
                    },
                    background_tasks=background_tasks,
                )
                raise HTTPException(status_code=404, detail="Card not found")

            if card_update.uid:
                db_card = await self.card_repos.find_by_uid(card_update.uid)
                if db_card and db_card.id != card_id:
                    # Log failure
                    self._log_event(
                        event_type=EventTypeEnum.ACCESS_DENIED,
                        metadata_desc={
                            "action": "update_card",
                            "reason": "Card with this UID already exists",
                            "uid": card_update.uid,
                        },
                        background_tasks=background_tasks,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Card with this UID already exists",
                    )

            # Check Membership if identity_id or issuer_organization_id is changing
            new_identity_id = card_update.identity_id or card.identity_id
            new_org_id = (
                card_update.issuer_organization_id or card.issuer_organization_id
            )

            if (
                new_identity_id
                and new_org_id
                and (card_update.identity_id or card_update.issuer_organization_id)
            ):
                await self._verify_membership(new_identity_id, new_org_id)

            update_data = card_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(card, key, value)

            updated = await self.card_repos.update(card)

            # Log assignment/unassignment if identity changed
            if card_update.identity_id is not None:
                new_id = card_update.identity_id
                # Note: this is a simple check, we could compare with old card if needed
                self._log_event(
                    event_type=(
                        EventTypeEnum.CARD_ASSIGNED
                        if new_id
                        else EventTypeEnum.CARD_UNASSIGNED
                    ),
                    card_id=updated.id,
                    metadata_desc={
                        "uid": updated.uid,
                        "action": "update_card_identity",
                        "identity_id": str(new_id) if new_id else None,
                    },
                    background_tasks=background_tasks,
                )

            return LazyCardReadSchema.model_validate(updated)
        except IntegrityError as e:
            print(e)
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                card_id=card_id,
                metadata_desc={
                    "action": "update_card",
                    "reason": "Integrity error",
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown identity id or issuer organization id",
            )
        except MembershipNotFoundException as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                card_id=card_id,
                metadata_desc={
                    "action": "update_card",
                    "reason": e.message,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except MembershipInactiveException as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                card_id=card_id,
                metadata_desc={
                    "action": "update_card",
                    "reason": e.message,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)

    async def delete_card(
        self, card_id: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        card = await self.card_repos.find_by_id(card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        # Log event before deletion or use ID
        self._log_event(
            event_type=EventTypeEnum.CARD_REVOKED,  # Or a specific DELETED enum if added
            metadata_desc={"uid": card.uid, "action": "delete_card"},
            background_tasks=background_tasks,
        )

        await self.card_repos.delete(card)

    async def delete_all_cards(self) -> None:
        await self.card_repos.delete_all()

    async def scan_card(
        self,
        card_uid: str,
        project_id: Any,
        reader_id: Optional[Any] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> ScanCardResponse:
        try:
            result = await self.card_repos.get_card_with_access_details(
                card_uid, project_id
            )

            card = result["card"]
            identity = result["identity"]
            membership = result["membership"]
            project = result["project"]

            # Extract Permissions (Roles from membership)
            permissions_list = (
                membership.roles if membership and membership.roles else []
            )

            # Log Success Event
            self._log_event(
                event_type=EventTypeEnum.ACCESS_GRANTED,
                card_id=card.id,
                reader_id=reader_id,
                project_id=project.id,
                metadata_desc={
                    "authorized": True,
                    "identity_id": str(identity.id),
                    "permissions": permissions_list,
                },
                background_tasks=background_tasks,
            )

            return ScanCardResponse(
                authorized=True,
                user=LazyIdentityReadSchema.model_validate(identity),
                permissions=permissions_list,
            )

        except CardNotFoundException as e:
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                reader_id=reader_id,
                project_id=project_id,
                metadata_desc={
                    "authorized": False,
                    "reason": e.message,
                    "card_uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except ProjectNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except IdentityNotAssignedException as e:
            # We know the card exists here because get_card_with_access_details would have
            # failed at CardNotFound otherwise. But we don't easily have the card_id here
            # without re-fetching or modifying the repo.
            # For now, let's log with what we have.
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                reader_id=reader_id,
                project_id=project_id,
                metadata_desc={
                    "authorized": False,
                    "reason": e.message,
                    "card_uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except CardInactiveException as e:
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                reader_id=reader_id,
                project_id=project_id,
                metadata_desc={
                    "authorized": False,
                    "reason": e.message,
                    "card_uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except UnauthorizedAccessException as e:
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                reader_id=reader_id,
                project_id=project_id,
                metadata_desc={
                    "authorized": False,
                    "reason": e.message,
                    "card_uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except MembershipNotFoundException as e:
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                reader_id=reader_id,
                project_id=project_id,
                metadata_desc={
                    "authorized": False,
                    "reason": e.message,
                    "card_uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except MembershipInactiveException as e:
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                reader_id=reader_id,
                project_id=project_id,
                metadata_desc={
                    "authorized": False,
                    "reason": e.message,
                    "card_uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except (
            CardAlreadyActiveException,
            InvalidActivationCodeException,
            ActivationCodeExpiredException,
        ) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )

    async def activate_card(
        self,
        request: CardActivationRequest,
        settings: Settings,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> CardActivationResponse:
        """
        Activates a card by linking it to an identity using an activation code.
        Atomicity is ensured by SQLAlchemy transaction management.
        """
        try:
            card = await self.card_repos.find_by_uid(request.card_uid)
            if not card:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "activate_card",
                        "reason": "Card not found",
                        "uid": request.card_uid,
                    },
                    background_tasks=background_tasks,
                )
                raise CardNotFoundException(request.card_uid)

            # 0. Check Membership in Issuer Organization
            await self._verify_membership(
                request.identity_id, card.issuer_organization_id
            )

            # 0b. Explicitly check if Identity exists to avoid confusing IntegrityErrors
            if self.identity_repos:
                identity = await self.identity_repos.find_by_id(request.identity_id)
                if not identity:
                    # Log failure
                    self._log_event(
                        event_type=EventTypeEnum.ACCESS_DENIED,
                        metadata_desc={
                            "action": "activate_card",
                            "reason": "Identity not found",
                            "identity_id": str(request.identity_id),
                            "uid": request.card_uid,
                        },
                        background_tasks=background_tasks,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"L'identité '{request.identity_id}' n'existe pas.",
                    )

            # 1. Check if already active
            if card.status == "active":
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    card_id=card.id,
                    metadata_desc={
                        "action": "activate_card",
                        "reason": "Card already active",
                        "uid": request.card_uid,
                    },
                    background_tasks=background_tasks,
                )
                raise CardAlreadyActiveException(request.card_uid)

            # 2. Validate Code
            if card.activation_code != request.activation_code:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    card_id=card.id,
                    metadata_desc={
                        "action": "activate_card",
                        "reason": "Invalid activation code",
                        "uid": request.card_uid,
                    },
                    background_tasks=background_tasks,
                )
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
                    # Log failure
                    self._log_event(
                        event_type=EventTypeEnum.ACCESS_DENIED,
                        card_id=card.id,
                        metadata_desc={
                            "action": "activate_card",
                            "reason": "Activation code expired",
                            "uid": request.card_uid,
                        },
                        background_tasks=background_tasks,
                    )
                    raise ActivationCodeExpiredException(request.card_uid)

            # 4. Atomic Update
            # Close existing active assignment if any (healing inconsistent state)
            existing_history = await self.card_repos.get_active_assignment(card.id)
            if existing_history:
                existing_history.unassigned_at = datetime.datetime.now(
                    datetime.timezone.utc
                ).replace(tzinfo=None)
                self.card_repos.db.add(existing_history)

            # Add new history record
            history = CardAssignmentHistory(
                card_id=card.id, identity_id=request.identity_id
            )
            self.card_repos.db.add(history)

            card.identity_id = request.identity_id
            card.status = "active"
            card.activation_code = None

            updated = await self.card_repos.update(card)

            # Log Activation Event
            self._log_event(
                event_type=EventTypeEnum.CARD_ACTIVATED,
                card_id=updated.id,
                metadata_desc={
                    "uid": updated.uid,
                    "identity_id": str(updated.identity_id),
                },
                background_tasks=background_tasks,
            )

            return CardActivationResponse(
                success=True, card=LazyCardReadSchema.model_validate(updated)
            )
        except IntegrityError as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "activate_card",
                    "reason": "Integrity error",
                    "uid": request.card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur d'intégrité base de données: {str(e.orig)}",
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
        except MembershipNotFoundException as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "activate_card",
                    "reason": e.message,
                    "uid": request.card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
        except MembershipInactiveException as e:
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "activate_card",
                    "reason": e.message,
                    "uid": request.card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)

    async def revoke_card(
        self, card_uid: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> CardActivationResponse:
        """
        Revokes a card by unlinking the identity and closing the history record.
        Resets card to pending with a new activation code.
        """
        try:
            card = await self.card_repos.find_by_uid(card_uid)
            if not card:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    metadata_desc={
                        "action": "revoke_card",
                        "reason": "Card not found",
                        "uid": card_uid,
                    },
                    background_tasks=background_tasks,
                )
                raise CardNotFoundException(card_uid)

            if card.status != "active" or not card.identity_id:
                # Log failure
                self._log_event(
                    event_type=EventTypeEnum.ACCESS_DENIED,
                    card_id=card.id,
                    metadata_desc={
                        "action": "revoke_card",
                        "reason": "Card not active or no identity assigned",
                        "uid": card_uid,
                    },
                    background_tasks=background_tasks,
                )
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

            # Log Revocation Event
            self._log_event(
                event_type=EventTypeEnum.CARD_REVOKED,
                card_id=updated.id,
                metadata_desc={"uid": updated.uid},
                background_tasks=background_tasks,
            )

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
            # Log failure
            self._log_event(
                event_type=EventTypeEnum.ACCESS_DENIED,
                metadata_desc={
                    "action": "revoke_card",
                    "reason": str(e),
                    "uid": card_uid,
                },
                background_tasks=background_tasks,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during revocation: {str(e)}",
            )

    @staticmethod
    def generate_activation_code() -> str:
        return secrets.token_urlsafe(16)
