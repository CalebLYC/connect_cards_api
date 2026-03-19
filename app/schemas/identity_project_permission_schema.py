from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class LazyIdentityProjectPermissionReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    allowed: bool = Field(..., example=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "allowed": True,
            }
        },
    )


class IdentityProjectPermissionCreateSchema(BaseModel):
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    allowed: Optional[bool] = Field(default=True, example=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "allowed": True,
            }
        },
    )


class IdentityProjectPermissionUpdateSchema(BaseModel):
    identity_id: Optional[UUID] = Field(
        default=None, example="04bcf3f5-cde5-4d27-8a20-2f50076043c5"
    )
    project_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    allowed: Optional[bool] = Field(default=None, example=False)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "allowed": False,
            }
        },
    )


from app.schemas.identity_schema import LazyIdentityReadSchema
from app.schemas.project_schema import LazyProjectReadSchema


class IdentityProjectPermissionReadSchema(BaseModel):

    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    allowed: bool = Field(..., example=True)
    identity: LazyIdentityReadSchema
    project: LazyProjectReadSchema

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "allowed": True,
                "identity": {
                    "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "email": "jdoe@example.com",
                    "name": "John Doe",
                    "created_at": "2025-01-01T00:00:00",
                },
                "project": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Example Project",
                    "description": "A sample project description",
                    "created_at": "2025-01-01T00:00:00",
                },
            }
        },
    )
