import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from uuid import UUID

from app.models.enums.sex_enum import SexEnum


class LazyIdentityReadSchema(BaseModel):
    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    email: EmailStr = Field(..., example="jdoe@example.com")
    name: str = Field(..., example="John Doe")
    sex: Optional[SexEnum] = Field(default=None, example=SexEnum.MALE.value)
    phone: Optional[str] = Field(default=None, example="+2250707070707")
    address: Optional[str] = Field(default=None, example="123 Rue de la Paix")
    date_of_birth: Optional[datetime.datetime] = Field(
        default=None, example="1990-01-01T00:00:00"
    )
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "email": "jdoe@example.com",
                "name": "John Doe",
                "sex": "M",
                "phone": "+2250707070707",
                "address": "123 Rue de la Paix",
                "date_of_birth": "1990-01-01T00:00:00",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


from app.schemas.card_schema import LazyCardReadSchema
from app.schemas.membership_schema import LazyMembershipReadSchema
from app.schemas.identity_project_permission_schema import (
    LazyIdentityProjectPermissionReadSchema,
)


class IdentityReadSchema(BaseModel):
    # from app.schemas.event_schema import LazyEventReadSchema
    # from app.schemas.card_assignment_history_schema import LazyCardAssignmentHistoryReadSchema

    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    email: EmailStr = Field(..., example="jdoe@example.com")
    name: str = Field(..., example="John Doe")
    sex: Optional[SexEnum] = Field(default=None, example=SexEnum.MALE.value)
    phone: Optional[str] = Field(default=None, example="+2250707070707")
    address: Optional[str] = Field(default=None, example="123 Rue de la Paix")
    date_of_birth: Optional[datetime.datetime] = Field(
        default=None, example="1990-01-01T00:00:00"
    )
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    cards: List[LazyCardReadSchema] = Field(default_factory=list)
    memberships: List[LazyMembershipReadSchema] = Field(default_factory=list)
    project_permissions: List[LazyIdentityProjectPermissionReadSchema] = Field(
        default_factory=list
    )
    # events: List[LazyEventReadSchema] = Field(default_factory=list)
    # card_assignment_history: List[LazyCardAssignmentHistoryReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "email": "jdoe@example.com",
                "name": "John Doe",
                "sex": "M",
                "phone": "+2250707070707",
                "address": "123 Rue de la Paix",
                "date_of_birth": "1990-01-01T00:00:00",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "cards": [
                    {
                        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "uid": "CARD123456",
                        "status": "active",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
                "memberships": [
                    {
                        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "status": "active",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
                "project_permissions": [
                    {
                        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                        "allowed": True,
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00",
                    }
                ],
                # "events": [],
                # "card_assignment_history": [],
            }
        },
    )


IdentityReadSchema.model_rebuild()


class IdentityCreateSchema(BaseModel):
    email: EmailStr = Field(..., example="jdoe@example.com")
    name: str = Field(..., example="John Doe")
    sex: Optional[SexEnum] = Field(default=None, example=SexEnum.MALE.value)
    phone: Optional[str] = Field(default=None, example="+2250707070707")
    address: Optional[str] = Field(default=None, example="123 Rue de la Paix")
    date_of_birth: Optional[datetime.datetime] = Field(
        default=None, example="1990-01-01T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "name": "John Doe",
                "sex": "M",
                "phone": "+2250707070707",
                "address": "123 Rue de la Paix",
                "date_of_birth": "1990-01-01T00:00:00",
            }
        },
    )


class IdentityUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None, example="jdoe@example.com")
    name: Optional[str] = Field(default=None, example="John Doe")
    sex: Optional[SexEnum] = Field(default=None, example=SexEnum.MALE.value)
    phone: Optional[str] = Field(default=None, example="+2250707070707")
    address: Optional[str] = Field(default=None, example="123 Rue de la Paix")
    date_of_birth: Optional[datetime.datetime] = Field(
        default=None, example="1990-01-01T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "name": "John Doe",
                "sex": "M",
                "phone": "+2250707070707",
                "address": "123 Rue de la Paix",
                "date_of_birth": "1990-01-01T00:00:00",
            }
        },
    )
