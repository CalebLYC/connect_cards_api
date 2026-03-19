import pytest
import asyncio
import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

from app.services.nfc.card_service import CardService
from app.repositories.card_repository import CardRepository
from app.models.card import Card
from app.models.card_assignment_history import CardAssignmentHistory
from app.exceptions.card_exceptions import (
    CardNotFoundException,
    CardNotActiveException,
)


@pytest.mark.asyncio
async def test_revoke_card_success():
    # Setup
    card_repos = MagicMock(spec=CardRepository)
    card_repos.db = MagicMock()
    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    card_id = uuid4()
    identity_id = uuid4()

    # Active card
    mock_card = Card(id=card_id, uid=card_uid, identity_id=identity_id, status="active")

    # Active history record
    mock_history = CardAssignmentHistory(
        card_id=card_id, identity_id=identity_id, assigned_at=datetime.datetime.now()
    )

    card_repos.find_by_uid = AsyncMock(return_value=mock_card)
    card_repos.get_active_assignment = AsyncMock(return_value=mock_history)
    card_repos.update = AsyncMock(return_value=mock_card)

    # Execute
    response = await service.revoke_card(card_uid)

    # Assert
    assert response.success is True
    assert mock_card.status == "pending"
    assert mock_card.identity_id is None
    assert mock_card.activation_code is not None  # Should be regenerated

    assert mock_history.unassigned_at is not None

    print("Success: test_revoke_card_success passed!")


@pytest.mark.asyncio
async def test_revoke_card_not_active():
    card_repos = MagicMock(spec=CardRepository)
    card_repos.db = MagicMock()
    service = CardService(card_repos=card_repos)

    card_uid = "CARD123"
    # Pending card (no identity)
    mock_card = Card(uid=card_uid, identity_id=None, status="pending")
    card_repos.find_by_uid = AsyncMock(return_value=mock_card)

    try:
        await service.revoke_card(card_uid)
        assert False, "Should have raised CardNotActiveException"
    except HTTPException as e:
        assert "not currently active" in e.detail
        print("Success: test_revoke_card_not_active passed!")


if __name__ == "__main__":
    asyncio.run(test_revoke_card_success())
    asyncio.run(test_revoke_card_not_active())
