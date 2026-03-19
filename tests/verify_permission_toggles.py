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
async def test_permission_toggles():
    # Setup
    repo = MagicMock(spec=IdentityProjectPermissionRepository)
    service = IdentityProjectPermissionService(permission_repos=repo)

    identity_id = uuid4()
    project_id = uuid4()

    # 1. Test Disallow (Existing -> False)
    mock_permission = IdentityProjectPermission(
        identity_id=identity_id, project_id=project_id, allowed=True
    )
    repo.find_by_identity_and_project = AsyncMock(return_value=mock_permission)
    repo.update = AsyncMock(return_value=mock_permission)

    res_disallow = await service.disallow_identity(str(identity_id), str(project_id))
    assert res_disallow.allowed is False
    print("Success: Disallow (existing) passed!")

    # 2. Test Allow (Existing -> True)
    mock_permission.allowed = False
    repo.find_by_identity_and_project = AsyncMock(return_value=mock_permission)

    res_allow = await service.allow_identity(str(identity_id), str(project_id))
    assert res_allow.allowed is True
    print("Success: Allow (existing) passed!")

    # 3. Test Proactive Disallow (New -> False)
    repo.find_by_identity_and_project = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=lambda p: p)

    res_new_disallow = await service.disallow_identity(
        str(identity_id), str(project_id)
    )
    assert res_new_disallow.allowed is False
    print("Success: Proactive Disallow (new) passed!")


if __name__ == "__main__":
    asyncio.run(test_permission_toggles())
