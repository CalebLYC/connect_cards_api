import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from uuid import UUID

from app.models.user import SexEnum


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(..., example="jdoe@example.com")
    password: str = Field(..., example="12345678")
    full_name: str = Field(..., example="John Doe")
    phone_number: Optional[str] = Field(default=None, example="90000000")
    sex: Optional[SexEnum] = Field(default=None, example="M")
    birthday_date: Optional[datetime.datetime] = Field(
        default=None, example="2004-01-01T00:00:00"
    )
    picture: Optional[str] = Field(
        default=None, example="https://example.com/picture.jpg"
    )
    locale: Optional[str] = Field(default=None, example="en-US")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "full_name": "John Doe",
                "password": "12345678",
                "phone_number": "90000000",
                "sex": "M",
                "birthday_date": "2004-01-01T00:00:00",
                "picture": "https://example.com/picture.jpg",
                "locale": "en-US",
            }
        },
    )


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None, example="jdoe@example.com")
    password: Optional[str] = Field(default=None, example="12345678")
    full_name: Optional[str] = Field(default=None, example="John Doe")
    phone_number: Optional[str] = Field(default=None, example="90000000")
    sex: Optional[SexEnum] = Field(default=None, example="F")
    birthday_date: Optional[datetime.datetime] = Field(
        default=None, example="2004-01-01T00:00:00"
    )
    is_active: Optional[bool] = Field(default=None, example=True)
    is_verified: Optional[bool] = Field(default=None, example=True)
    picture: Optional[str] = Field(
        default=None, example="https://example.com/picture.jpg"
    )
    locale: Optional[str] = Field(default=None, example="en-US")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "full_name": "John Doe",
                "password": "12345678",
                "phone_number": "90000000",
                "sex": "F",
                "birthday_date": "2004-01-01T00:00:00",
                "is_active": True,
                "is_verified": True,
                "picture": "https://example.com/picture.jpg",
                "locale": "en-US",
            }
        },
    )


class UserReadSchema(BaseModel):
    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    email: EmailStr = Field(..., example="jdoe@example.com")
    full_name: Optional[str] = Field(default=None, example="John Doe")
    phone_number: Optional[str] = Field(default=None, example="90000000")
    sex: Optional[SexEnum] = Field(default=None, example="M")
    birthday_date: Optional[datetime.datetime] = Field(
        default=None, example="2004-01-01T00:00:00"
    )
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    is_active: bool = Field(default=True, example=True)
    is_verified: bool = Field(default=False, example=False)
    picture: Optional[str] = Field(
        default=None, example="https://example.com/picture.jpg"
    )
    locale: Optional[str] = Field(default=None, example="en-US")
    roles: List[str] = Field(default=[], example=["user"])
    permissions: List[str] = Field(default=[], example=["user:read"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
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
            }
        },
    )
