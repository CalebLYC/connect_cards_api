from fastapi import APIRouter, Depends, status, Query, Path
from typing import List, Optional

from app.providers.auth_provider import require_permission, require_role
from app.providers.service_providers import get_project_service
from app.schemas.project_schema import (
    ProjectReadSchema,
    LazyProjectReadSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
)
from app.services.nfc.project_service import ProjectService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[require_permission("project:manage", verify_org=True)],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[ProjectReadSchema],
    summary="List projects",
    dependencies=[require_permission("project:read", verify_org=True)],
)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    eager: bool = Query(True),
    service: ProjectService = Depends(get_project_service),
):
    return await service.list_projects(
        skip=skip, limit=limit, organization_id=organization_id, name=name, eager=eager
    )


@router.get(
    "/{project_id}", response_model=ProjectReadSchema, summary="Get project by ID"
)
async def get_project(
    project_id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_project(project_id, eager=eager)


@router.post(
    "/",
    response_model=LazyProjectReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
async def create_project(
    project_create: ProjectCreateSchema,
    service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(project_create)


@router.put(
    "/{project_id}", response_model=LazyProjectReadSchema, summary="Update project"
)
async def update_project(
    project_id: str = Path(..., min_length=24, max_length=36),
    project_update: ProjectUpdateSchema = ...,
    service: ProjectService = Depends(get_project_service),
):
    return await service.update_project(project_id, project_update)


@router.delete(
    "/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete project"
)
async def delete_project(
    project_id: str = Path(..., min_length=24, max_length=36),
    service: ProjectService = Depends(get_project_service),
):
    await service.delete_project(project_id)
    return {"detail": "Project deleted"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all projects",
    dependencies=[require_role("superadmin")],
)
async def delete_all_projects(
    service: ProjectService = Depends(get_project_service),
):
    await service.delete_all_projects()
    return {"detail": "All projects deleted"}
