from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.identity_repository import IdentityRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.repositories.permission_repository import PermissionRepository

# NFC Repositories
from app.repositories.card_repository import CardRepository
from app.repositories.reader_repository import ReaderRepository
from app.repositories.event_repository import EventRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.card_assignment_history_repository import (
    CardAssignmentHistoryRepository,
)
from app.repositories.membership_repository import MembershipRepository
from app.repositories.identity_project_permission_repository import (
    IdentityProjectPermissionRepository,
)
from app.repositories.webhook_repository import WebhookRepository

from app.providers.providers import get_db


def get_webhook_repository(db: AsyncSession = Depends(get_db)):
    return WebhookRepository(db=db)


def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db=db)


def get_identity_repository(db: AsyncSession = Depends(get_db)):
    return IdentityRepository(db=db)


def get_access_token_repository(db: AsyncSession = Depends(get_db)):
    return AccessTokenRepository(db=db)


def get_role_repository(db: AsyncSession = Depends(get_db)):
    return RoleRepository(db=db)


def get_permission_repository(db: AsyncSession = Depends(get_db)):
    return PermissionRepository(db=db)


# NFC Repository Providers
def get_card_repository(db: AsyncSession = Depends(get_db)):
    return CardRepository(db=db)


def get_reader_repository(db: AsyncSession = Depends(get_db)):
    return ReaderRepository(db=db)


def get_event_repository(db: AsyncSession = Depends(get_db)):
    return EventRepository(db=db)


def get_organization_repository(db: AsyncSession = Depends(get_db)):
    return OrganizationRepository(db=db)


def get_project_repository(db: AsyncSession = Depends(get_db)):
    return ProjectRepository(db=db)


def get_card_assignment_history_repository(db: AsyncSession = Depends(get_db)):
    return CardAssignmentHistoryRepository(db=db)


def get_membership_repository(db: AsyncSession = Depends(get_db)):
    return MembershipRepository(db=db)


def get_identity_project_permission_repository(db: AsyncSession = Depends(get_db)):
    return IdentityProjectPermissionRepository(db=db)


def get_webhook_repository(db: AsyncSession = Depends(get_db)):
    return WebhookRepository(db=db)
