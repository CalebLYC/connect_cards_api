import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID

from app.schemas.permission_schema import PermissionReadSchema


class RoleCreateSchema(BaseModel):
    name: str = Field(example="user")
    description: str = Field(example="description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "user",
                "description": "description",
            }
        },
    )


class RoleUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, example="user")
    description: Optional[str] = Field(default=None, example="description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "user",
                "description": "description",
            }
        },
    )


class RoleReadSchema(BaseModel):
    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    name: str = Field(example="user")
    description: str = Field(example="description")
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    permissions: List[PermissionReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "name": "user",
                "description": "description",
                "created_at": "2025-01-01T00:00:00",
                "permissions": ["user:read"],
            }
        },
    )
