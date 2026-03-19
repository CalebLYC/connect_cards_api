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
from app.schemas.nfc_schema import CardActivationRequest
from app.core.config import Settings
from app.exceptions.card_exceptions import (
    CardNotFoundException,
    CardAlreadyActiveException,
    InvalidActivationCodeException,
    ActivationCodeExpiredException,
)


@pytest.mark.asyncio
async def test_activate_card_success():
    # Setup
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)
    settings = MagicMock(spec=Settings)
    settings.activation_code_expiry_minutes = 1440

    card_uid = "CARD123"
    activation_code = "SECRET123"
    identity_id = uuid4()

    mock_card = Card(
        uid=card_uid,
        activation_code=activation_code,
        status="pending",
        created_at=datetime.datetime.now(),
    )

    card_repos.find_by_uid = AsyncMock(return_value=mock_card)
    card_repos.update = AsyncMock(return_value=mock_card)

    request = CardActivationRequest(
        card_uid=card_uid, activation_code=activation_code, identity_id=identity_id
    )

    # Execute
    response = await service.activate_card(request, settings)

    # Assert
    assert response.success is True
    assert mock_card.status == "active"
    assert mock_card.identity_id == identity_id
    assert mock_card.activation_code is None

    # Check if history was added to session
    added_objects = card_repos.db.add.call_args_list
    history_found = False
    for call in added_objects:
        obj = call[0][0]
        if isinstance(obj, CardAssignmentHistory):
            assert obj.card_id == mock_card.id
            assert obj.identity_id == identity_id
            history_found = True
            break
    assert history_found, "CardAssignmentHistory record was not added to the session"

    print("Success: test_activate_card_success passed!")


@pytest.mark.asyncio
async def test_activate_card_invalid_code():
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)
    settings = MagicMock(spec=Settings)

    card_uid = "CARD123"
    mock_card = Card(uid=card_uid, activation_code="REAL_CODE", status="pending")
    card_repos.find_by_uid = AsyncMock(return_value=mock_card)

    request = CardActivationRequest(
        card_uid=card_uid, activation_code="WRONG_CODE", identity_id=uuid4()
    )

    try:
        await service.activate_card(request, settings)
        assert False, "Should have raised InvalidActivationCodeException"
    except InvalidActivationCodeException:
        print("Success: test_activate_card_invalid_code passed!")


@pytest.mark.asyncio
async def test_activate_card_expired():
    card_repos = MagicMock(spec=CardRepository)
    service = CardService(card_repos=card_repos)
    settings = MagicMock(spec=Settings)
    settings.activation_code_expiry_minutes = 60  # 1 hour

    card_uid = "CARD123"
    # Created 2 hours ago
    created_at = datetime.datetime.now() - datetime.timedelta(hours=2)
    mock_card = Card(
        uid=card_uid, activation_code="CODE", status="pending", created_at=created_at
    )
    card_repos.find_by_uid = AsyncMock(return_value=mock_card)

    request = CardActivationRequest(
        card_uid=card_uid, activation_code="CODE", identity_id=uuid4()
    )

    try:
        await service.activate_card(request, settings)
        assert False, "Should have raised ActivationCodeExpiredException"
    except ActivationCodeExpiredException:
        print("Success: test_activate_card_expired passed!")


if __name__ == "__main__":
    asyncio.run(test_activate_card_success())
    asyncio.run(test_activate_card_invalid_code())
    asyncio.run(test_activate_card_expired())
