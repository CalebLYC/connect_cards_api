from fastapi import APIRouter,  Depends
from app.providers.service_providers import get_setup_service
from app.services.setup_service import SetupService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/setup",
    tags=["Setup"],
    dependencies=[],
    responses=http_status.router_responses,
)


@router.post(
    "/superadmin",
    response_model=dict,
    summary="Create superadmin user",
)
async def create_superadmin(
    service: SetupService = Depends(get_setup_service),
):
   
    """Set up the superadmin user.

    Args:
        service (SetupService, optional): Setup service dependency.

    Returns:
        dict: Success message."""
    return await service.setup_superadmin()


@router.post(
    "/roles-and-permissions",
    response_model=dict,
    summary="Create roles and permissions",
)
async def create_roles_and_permissions(
    service: SetupService = Depends(get_setup_service),
):
   
    """Set up roles and permissions.

    Args:
        service (SetupService, optional): Setup service dependency.

    Returns:
        dict: Success message."""
    return await service.setup_roles_and_permissions()