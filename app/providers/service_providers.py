from fastapi import Depends
from app.core.config import Settings
from app.providers.providers import get_settings
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.identity_repository import IdentityRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.repositories.permission_repository import PermissionRepository

# NFC Repositories (for service dependency injection)
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

# NFC Services
from app.services.nfc.card_service import CardService
from app.services.nfc.reader_service import ReaderService
from app.services.nfc.event_service import EventService
from app.services.nfc.organization_service import OrganizationService
from app.services.nfc.project_service import ProjectService
from app.services.nfc.card_assignment_history_service import (
    CardAssignmentHistoryService,
)
from app.services.nfc.membership_service import MembershipService
from app.services.nfc.identity_project_permission_service import (
    IdentityProjectPermissionService,
)
from app.services.nfc.webhook_service import WebhookService
from app.services.nfc.event_dispatcher import EventDispatcher

from app.services.nfc.identity_service import IdentityService
from app.services.auth.permission_service import PermissionService
from app.providers.repository_providers import (
    get_access_token_repository,
    get_role_repository,
    get_user_repository,
    get_permission_repository,
    get_identity_repository,
    # NFC Repository Providers
    get_card_repository,
    get_reader_repository,
    get_event_repository,
    get_organization_repository,
    get_project_repository,
    get_card_assignment_history_repository,
    get_membership_repository,
    get_identity_project_permission_repository,
    get_webhook_repository,
)
from app.services.auth.auth_service import AuthService
from app.services.auth.role_service import RoleService
from app.services.auth.user_service import UserService
from app.services.setup_service import SetupService


def get_user_service(
    user_repos: UserRepository = Depends(get_user_repository),
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> UserService:
    return UserService(
        user_repos=user_repos, role_repos=role_repos, permission_repos=permission_repos
    )


def get_webhook_service(
    webhook_repos: WebhookRepository = Depends(get_webhook_repository),
) -> WebhookService:
    return WebhookService(webhook_repos=webhook_repos)


def get_event_dispatcher(
    webhook_repos: WebhookRepository = Depends(get_webhook_repository),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> EventDispatcher:
    return EventDispatcher(webhook_repos=webhook_repos, webhook_service=webhook_service)


def get_identity_service(
    identity_repos: IdentityRepository = Depends(get_identity_repository),
    event_repos: EventRepository = Depends(get_event_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> IdentityService:
    return IdentityService(
        identity_repos=identity_repos,
        event_repos=event_repos,
        event_dispatcher=event_dispatcher,
    )


def get_auth_service(
    user_repos: UserRepository = Depends(get_user_repository),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> AuthService:
    return AuthService(user_repos=user_repos, access_token_repos=access_token_repos)


def get_role_service(
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> RoleService:
    return RoleService(role_repos=role_repos, permission_repos=permission_repos)


def get_permission_service(
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> PermissionService:
    return PermissionService(permission_repos=permission_repos)


def get_setup_service(
    user_repos: UserRepository = Depends(get_user_repository),
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
    settings: Settings = Depends(get_settings),
) -> SetupService:
    return SetupService(
        user_repos=user_repos,
        role_repos=role_repos,
        permission_repos=permission_repos,
        settings=settings,
    )


# NFC Service Providers
def get_card_service(
    card_repos: CardRepository = Depends(get_card_repository),
    membership_repos: MembershipRepository = Depends(get_membership_repository),
    identity_repos: IdentityRepository = Depends(get_identity_repository),
    event_repos: EventRepository = Depends(get_event_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> CardService:
    return CardService(
        card_repos=card_repos,
        membership_repos=membership_repos,
        identity_repos=identity_repos,
        event_repos=event_repos,
        event_dispatcher=event_dispatcher,
    )


def get_reader_service(
    reader_repos: ReaderRepository = Depends(get_reader_repository),
    project_repos: ProjectRepository = Depends(get_project_repository),
    organization_repos: OrganizationRepository = Depends(get_organization_repository),
    event_repos: EventRepository = Depends(get_event_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> ReaderService:
    return ReaderService(
        reader_repos=reader_repos,
        project_repos=project_repos,
        organization_repos=organization_repos,
        event_repos=event_repos,
        event_dispatcher=event_dispatcher,
    )


def get_event_service(
    event_repos: EventRepository = Depends(get_event_repository),
    reader_repos: ReaderRepository = Depends(get_reader_repository),
    project_repos: ProjectRepository = Depends(get_project_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> EventService:
    return EventService(
        event_repos=event_repos,
        reader_repos=reader_repos,
        project_repos=project_repos,
        event_dispatcher=event_dispatcher,
    )


def get_organization_service(
    organization_repos: OrganizationRepository = Depends(get_organization_repository),
) -> OrganizationService:
    return OrganizationService(organization_repos=organization_repos)


def get_project_service(
    project_repos: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
    return ProjectService(project_repos=project_repos)


def get_card_assignment_history_service(
    history_repos: CardAssignmentHistoryRepository = Depends(
        get_card_assignment_history_repository
    ),
) -> CardAssignmentHistoryService:
    return CardAssignmentHistoryService(history_repos=history_repos)


def get_membership_service(
    membership_repos: MembershipRepository = Depends(get_membership_repository),
    event_repos: EventRepository = Depends(get_event_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> MembershipService:
    return MembershipService(
        membership_repos=membership_repos,
        event_repos=event_repos,
        event_dispatcher=event_dispatcher,
    )


def get_identity_project_permission_service(
    permission_repos: IdentityProjectPermissionRepository = Depends(
        get_identity_project_permission_repository
    ),
    project_repos: ProjectRepository = Depends(get_project_repository),
    membership_repos: MembershipRepository = Depends(get_membership_repository),
    event_repos: EventRepository = Depends(get_event_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> IdentityProjectPermissionService:
    return IdentityProjectPermissionService(
        permission_repos=permission_repos,
        project_repos=project_repos,
        membership_repos=membership_repos,
        event_repos=event_repos,
        event_dispatcher=event_dispatcher,
    )
