import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional
from app.schemas.user_schema import UserReadSchema


class AccessTokenBaseSchema(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    expires_at: Optional[datetime.datetime] = Field(default=None)
    revoked: bool = Field(default=False)


class AccessTokenCreateSchema(AccessTokenBaseSchema):
    user_id: UUID = Field(...)


class AccessTokenReadSchema(AccessTokenBaseSchema):
    id: UUID
    # user: UserReadSchema
    created_at: datetime.datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user": {
                    "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "email": "jdoe@example.com",
                    "full_name": "John Doe",
                    "phone_number": "90000000",
                    "sex": "M",
                    "birthday_date": "2004-01-01T00:00:00",
                    "created_at": "2025-01-01T00:00:00",
                    "is_active": True,
                    "is_verified": False,
                    "picture": "https://example.com/picture.jpg",
                    "locale": "en-US",
                    "roles": ["user"],
                    "permissions": ["user:read"],
                },
                "created_at": "2023-10-01T12:00:00Z",
            }
        },
    )
