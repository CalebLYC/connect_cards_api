import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

from app.services.nfc.identity_project_permission_service import (
    IdentityProjectPermissionService,
)
from app.repositories.identity_project_permission_repository import (
    IdentityProjectPermissionRepository,
)
from app.models.identity_project_permission import IdentityProjectPermission


@pytest.mark.asyncio
async def test_disallow_identity_existing_record():
    # Setup
    repo = MagicMock(spec=IdentityProjectPermissionRepository)
    service = IdentityProjectPermissionService(permission_repos=repo)

    identity_id = uuid4()
    project_id = uuid4()

    # Existing "allowed" permission
    mock_permission = IdentityProjectPermission(
        identity_id=identity_id, project_id=project_id, allowed=True
    )

    repo.find_by_identity_and_project = AsyncMock(return_value=mock_permission)
    repo.update = AsyncMock(return_value=mock_permission)

    # Execute
    result = await service.disallow_identity(str(identity_id), str(project_id))

    # Assert
    assert result.allowed is False
    assert mock_permission.allowed is False
    repo.update.assert_called_once_with(mock_permission)
    print("Success: test_disallow_identity_existing_record passed!")


@pytest.mark.asyncio
async def test_disallow_identity_new_record():
    # Setup
    repo = MagicMock(spec=IdentityProjectPermissionRepository)
    service = IdentityProjectPermissionService(permission_repos=repo)

    identity_id = uuid4()
    project_id = uuid4()

    # No existing record
    repo.find_by_identity_and_project = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=lambda p: p)  # Return the input object

    # Execute
    result = await service.disallow_identity(str(identity_id), str(project_id))

    # Assert
    assert result.allowed is False
    # Check if create was called with a permission where allowed=False
    call_args = repo.create.call_args[0][0]
    assert call_args.identity_id == identity_id
    assert call_args.project_id == project_id
    assert call_args.allowed is False
    print("Success: test_disallow_identity_new_record passed!")


if __name__ == "__main__":
    asyncio.run(test_disallow_identity_existing_record())
    asyncio.run(test_disallow_identity_new_record())
