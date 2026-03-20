import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID


class LazyMembershipReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    roles: Optional[List[str]] = Field(default=None, example=["member"])
    status: str = Field(..., example="active")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "roles": ["member"],
                "status": "active",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


class MembershipCreateSchema(BaseModel):
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    roles: Optional[List[str]] = Field(default=None, example=["member"])
    status: Optional[str] = Field(default="active", example="active")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "roles": ["member"],
                "status": "active",
            }
        },
    )


class MembershipUpdateSchema(BaseModel):
    identity_id: Optional[UUID] = Field(
        default=None, example="04bcf3f5-cde5-4d27-8a20-2f50076043c5"
    )
    organization_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    roles: Optional[List[str]] = Field(default=None, example=["admin"])
    status: Optional[str] = Field(default=None, example="inactive")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "roles": ["admin"],
                "status": "inactive",
            }
        },
    )


from app.schemas.identity_schema import LazyIdentityReadSchema
from app.schemas.organization_schema import LazyOrganizationReadSchema


class MembershipReadSchema(BaseModel):

    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    roles: Optional[List[str]] = Field(default=None, example=["member"])
    status: str = Field(..., example="active")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    identity: LazyIdentityReadSchema
    organization: LazyOrganizationReadSchema

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "roles": ["member"],
                "status": "active",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "identity": {
                    "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "email": "jdoe@example.com",
                    "name": "John Doe",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
                "organization": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Example Organization",
                    "type": "Company",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
            }
        },
    )
