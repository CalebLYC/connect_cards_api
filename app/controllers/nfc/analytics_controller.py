from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_event_service
from app.services.nfc.event_service import EventService
from app.schemas.analytics_schema import (
    AnalyticsSummarySchema,
    DailyScanSchema,
    TopCardSchema,
    DenialRateSchema,
)
from app.utils.constants import http_status

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses=http_status.router_responses,
)


@router.get(
    "/summary",
    response_model=AnalyticsSummarySchema,
    summary="Get analytics summary for an organization",
    dependencies=[require_permission("event:read", verify_org=True)],
)
async def get_analytics_summary(
    organization_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: EventService = Depends(get_event_service),
):
    """
    Returns aggregated analytics for an organization.
    If the requester is a superadmin and organization_id is None, it returns global analytics.
    """
    return await service.get_analytics(
        organization_id=organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/global/health",
    summary="Get global system health metrics",
    dependencies=[require_role("admin")],
)
async def get_global_health(
    service: EventService = Depends(get_event_service),
):
    """
    Returns high-level system metrics. Restricted to system administrators.
    """
    return await service.get_system_health()
