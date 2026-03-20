import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID

from app.models.enums.organization_type_enum import OrganizationTypeEnum


class LazyOrganizationReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: str = Field(..., example="Example Organization")
    identification_number: str = Field(..., example="ORG-123456789")
    url: Optional[str] = Field(default=None, example="https://example.com")
    type: Optional[OrganizationTypeEnum] = Field(default=None, example="Company")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Example Organization",
                "identification_number": "ORG-123456789",
                "url": "https://example.com",
                "type": "Company",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


class OrganizationCreateSchema(BaseModel):
    name: str = Field(..., example="Example Organization")
    identification_number: str = Field(..., example="ORG-123456789")
    url: Optional[str] = Field(default=None, example="https://example.com")
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
    identification_number: Optional[str] = Field(default=None, example="ORG-123456789")
    url: Optional[str] = Field(default=None, example="https://example.com")
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
    identification_number: str = Field(..., example="ORG-123456789")
    url: Optional[str] = Field(default=None, example="https://example.com")
    type: Optional[OrganizationTypeEnum] = Field(default=None, example="Company")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
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
                "identification_number": "ORG-123456789",
                "url": "https://example.com",
                "type": "Company",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "users": [
                    {
                        "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                        "email": "jdoe@example.com",
                        "name": "John Doe",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
                # "memberships": [],
                "projects": [
                    {
                        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "name": "Example Project",
                        "description": "A sample project description",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
                "readers": [
                    {
                        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "name": "Example Reader",
                        "description": "A sample reader description",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
                "issued_cards": [
                    {
                        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "name": "Example Card",
                        "description": "A sample card description",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
            }
        },
    )


OrganizationReadSchema.model_rebuild()
