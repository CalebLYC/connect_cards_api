# app/schemas/permission_schema.py
import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class PermissionCreateSchema(BaseModel):
    code: str = Field(example="user:read")
    description: str = Field(example="Can read user data")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "code": "user:read",
                "description": "Can read user data",
            }
        },
    )


class PermissionUpdateSchema(BaseModel):
    code: Optional[str] = Field(default=None, example="user:read")
    description: Optional[str] = Field(default=None, example="Can read user data")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "code": "user:read",
                "description": "Can read user data",
            }
        },
    )


class PermissionReadSchema(BaseModel):
    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    code: str = Field(example="user:read")
    description: str = Field(example="Can read user data")
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "code": "user:read",
                "description": "Can read user data",
                "created_at": "2025-01-01T00:00:00",
            }
        },
    )
