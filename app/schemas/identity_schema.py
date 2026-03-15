import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import  Optional
from uuid import UUID


class IdentityCreateSchema(BaseModel):
    email: EmailStr = Field(..., example="jdoe@example.com")
    name: str = Field(..., example="John Doe")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "name": "John Doe",
            }
        },
    )


class IdentityUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None, example="jdoe@example.com")
    name: Optional[str] = Field(default=None, example="John Doe")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "full_name": "John Doe",
            }
        },
    )


class IdentityReadSchema(BaseModel):
    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    email: EmailStr = Field(..., example="jdoe@example.com")
    name: str = Field(..., example="John Doe")
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "email": "jdoe@example.com",
                "name": "John Doe",
                "created_at": "2025-01-01T00:00:00",
            }
        },
    )
