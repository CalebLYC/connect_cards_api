from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.organization import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization_schema import (
    OrganizationReadSchema,
    LazyOrganizationReadSchema,
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
)


class OrganizationService:
    def __init__(self, organization_repos: OrganizationRepository):
        self.organization_repos = organization_repos

    async def get_organization(
        self, organization_id: str, eager: bool = True
    ) -> Optional[OrganizationReadSchema]:
        if eager:
            organization = await self.organization_repos.find_by_id_eager(
                organization_id
            )
        else:
            organization = await self.organization_repos.find_by_id(organization_id)

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )
        return OrganizationReadSchema.model_validate(organization)

    async def list_organizations(
        self,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        eager: bool = False,
    ) -> List[OrganizationReadSchema]:
        if eager:
            organizations = await self.organization_repos.find_many_eager(
                filters, skip, limit
            )
        else:
            organizations = await self.organization_repos.find_many(
                filters, skip, limit
            )
        return [OrganizationReadSchema.model_validate(o) for o in organizations]

    async def create_organization(
        self, organization_create: OrganizationCreateSchema
    ) -> LazyOrganizationReadSchema:
        try:
            organization_model = Organization(**organization_create.model_dump())
            created = await self.organization_repos.create(organization_model)
            return LazyOrganizationReadSchema.model_validate(created)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization already exists",
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_organization(
        self, organization_id: str, organization_update: OrganizationUpdateSchema
    ) -> LazyOrganizationReadSchema:
        organization = await self.organization_repos.find_by_id(organization_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        update_data = organization_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(organization, key, value)

        updated = await self.organization_repos.update(organization)
        return LazyOrganizationReadSchema.model_validate(updated)

    async def delete_organization(self, organization_id: str) -> None:
        organization = await self.organization_repos.find_by_id(organization_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        await self.organization_repos.delete(organization)

    async def delete_all_organizations(self) -> None:
        await self.organization_repos.delete_all()
