import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID

from app.models.organization import OrganizationTypeEnum


class LazyOrganizationReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: str = Field(..., example="Example Organization")
    type: Optional[OrganizationTypeEnum] = Field(default=None, example="Company")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Example Organization",
                "type": "Company",
                "created_at": "2025-01-01T00:00:00",
            }
        },
    )


class OrganizationCreateSchema(BaseModel):
    name: str = Field(..., example="Example Organization")
    type: Optional[OrganizationTypeEnum] = Field(
        default=OrganizationTypeEnum.COMPANY, example="Company"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Example Organization",
                "type": "Company",
            }
        },
    )


class OrganizationUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, example="Example Organization")
    type: Optional[OrganizationTypeEnum] = Field(default=None, example="Company")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Example Organization",
                "type": "Company",
            }
        },
    )


from app.schemas.user_schema import LazyUserReadSchema
from app.schemas.project_schema import LazyProjectReadSchema
from app.schemas.reader_schema import LazyReaderReadSchema
from app.schemas.card_schema import LazyCardReadSchema

# from app.schemas.membership_schema import LazyMembershipReadSchema


class OrganizationReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: str = Field(..., example="Example Organization")
    type: Optional[OrganizationTypeEnum] = Field(default=None, example="Company")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    users: List[LazyUserReadSchema] = Field(default_factory=list)
    # memberships: List[LazyMembershipReadSchema] = Field(default_factory=list)
    projects: List[LazyProjectReadSchema] = Field(default_factory=list)
    readers: List[LazyReaderReadSchema] = Field(default_factory=list)
    issued_cards: List[LazyCardReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Example Organization",
                "type": "Company",
                "created_at": "2025-01-01T00:00:00",
                "users": [],
                # "memberships": [],
                "projects": [],
                "readers": [],
                "issued_cards": [],
            }
        },
    )
