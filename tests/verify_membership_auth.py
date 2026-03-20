import asyncio
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.nfc.card_service import CardService
from app.repositories.card_repository import CardRepository
from app.repositories.membership_repository import MembershipRepository
from app.exceptions.card_exceptions import (
    MembershipNotFoundException,
    MembershipInactiveException,
    UnauthorizedAccessException,
)
from app.schemas.nfc_schema import CardActivationRequest


@pytest.mark.asyncio
async def test_card_activation_requires_membership():
    # Mock repositories
    card_repos = AsyncMock(spec=CardRepository)
    membership_repos = AsyncMock(spec=MembershipRepository)

    service = CardService(card_repos=card_repos, membership_repos=membership_repos)

    # Setup mock data
    card_uid = "CARD123"
    org_id = uuid.uuid4()
    identity_id = uuid.uuid4()

    mock_card = MagicMock()
    mock_card.uid = card_uid
    mock_card.issuer_organization_id = org_id
    mock_card.status = "pending"
    mock_card.activation_code = "SECRET"

    card_repos.find_by_uid.return_value = mock_card

    # Case 1: No membership
    membership_repos.find_by_identity_and_organization.return_value = None

    request = CardActivationRequest(
        card_uid=card_uid, activation_code="SECRET", identity_id=identity_id
    )

    with pytest.raises(HTTPException) as excinfo:
        await service.activate_card(
            request, MagicMock(card_activation_code_expiry_minutes=60)
        )

    assert excinfo.value.status_code == 403
    assert "no membership" in excinfo.value.detail.lower()


@pytest.mark.asyncio
async def test_scan_card_requires_active_membership():
    # Mock repository
    card_repos = AsyncMock(spec=CardRepository)
    # Note: get_card_with_access_details is in CardRepository

    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    project_id = uuid.uuid4()

    # Simulate repository raising MembershipNotFoundException
    card_repos.get_card_with_access_details.side_effect = MembershipNotFoundException(
        uuid.uuid4(), uuid.uuid4()
    )

    with pytest.raises(HTTPException) as excinfo:
        await service.scan_card(card_uid, project_id)

    assert excinfo.value.status_code == 403
    assert "no membership" in excinfo.value.detail.lower()


if __name__ == "__main__":
    import sys

    pytest.main(sys.argv)
