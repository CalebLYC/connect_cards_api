import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from app.repositories.card_repository import CardRepository
from app.models.card import Card
from app.models.identity import Identity
from app.models.identity_project_permission import IdentityProjectPermission
from app.models.membership import Membership
from app.exceptions.card_exceptions import (
    CardNotFoundException,
    UnauthorizedAccessException,
    CardInactiveException,
    IdentityNotAssignedException,
    ProjectNotFoundException,
)
from app.services.nfc.card_service import CardService


@pytest.mark.asyncio
async def test_scan_card_success():
    # Setup
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    project_id = uuid4()
    identity_id = uuid4()

    mock_card = Card(uid=card_uid, identity_id=identity_id, status="active")
    mock_identity = Identity(id=identity_id, name="Test User", email="test@example.com")
    mock_permission = IdentityProjectPermission(
        identity_id=identity_id, project_id=project_id, allowed=True
    )
    mock_membership = Membership(identity_id=identity_id, roles=["admin"])

    card_repos.get_card_with_access_details = AsyncMock(
        return_value={
            "card": mock_card,
            "identity": mock_identity,
            "permission": mock_permission,
            "membership": mock_membership,
        }
    )

    # Execute
    response = await service.scan_card(card_uid, project_id)

    # Assert
    assert response.authorized is True
    assert response.user.id == identity_id
    assert response.permissions == ["admin"]
    print("Success: test_scan_card_success passed!")


@pytest.mark.asyncio
async def test_scan_card_inactive():
    # Setup
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    project_id = uuid4()
    identity_id = uuid4()

    mock_card = Card(uid=card_uid, identity_id=identity_id, status="pending")

    card_repos.get_card_with_access_details = AsyncMock(
        side_effect=CardInactiveException(card_uid)
    )

    # Execute & Assert
    try:
        await service.scan_card(card_uid, project_id)
        assert False, "Should have raised HTTPException for inactive card"
    except HTTPException as e:
        assert e.status_code == 403
        assert "inactive" in e.detail
        print("Success: test_scan_card_inactive passed!")


@pytest.mark.asyncio
async def test_scan_card_unauthorized():
    # Setup
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    project_id = uuid4()
    identity_id = uuid4()

    mock_card = Card(uid=card_uid, identity_id=identity_id, status="active")
    mock_identity = Identity(id=identity_id)
    mock_permission = IdentityProjectPermission(
        identity_id=identity_id, project_id=project_id, allowed=False
    )

    card_repos.get_card_with_access_details = AsyncMock(
        side_effect=UnauthorizedAccessException(identity_id, project_id)
    )

    # Execute & Assert
    try:
        await service.scan_card(card_uid, project_id)
        assert False, "Should have raised HTTPException for unauthorized"
    except HTTPException as e:
        assert e.status_code == 403
        assert "unauthorized" in e.detail or "unauthorized" in str(e).lower()
        print("Success: test_scan_card_unauthorized passed!")


@pytest.mark.asyncio
async def test_scan_card_not_assigned():
    # Setup
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    project_id = uuid4()

    mock_card = Card(uid=card_uid, identity_id=None, status="active")

    card_repos.get_card_with_access_details = AsyncMock(
        side_effect=IdentityNotAssignedException(card_uid)
    )

    # Execute & Assert
    try:
        await service.scan_card(card_uid, project_id)
        assert False, "Should have raised HTTPException for unassigned card"
    except HTTPException as e:
        assert e.status_code == 404
        assert "assigned" in e.detail or "assigned" in str(e).lower()
        print("Success: test_scan_card_not_assigned passed!")


if __name__ == "__main__":
    asyncio.run(test_scan_card_success())
    asyncio.run(test_scan_card_inactive())
    asyncio.run(test_scan_card_unauthorized())
    asyncio.run(test_scan_card_not_assigned())
