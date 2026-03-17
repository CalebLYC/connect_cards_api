import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from uuid import UUID



class LazyIdentityReadSchema(BaseModel):
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


from app.schemas.card_schema import LazyCardReadSchema
from app.schemas.membership_schema import LazyMembershipReadSchema
from app.schemas.identity_project_permission_schema import LazyIdentityProjectPermissionReadSchema
class IdentityReadSchema(BaseModel):
    #from app.schemas.event_schema import LazyEventReadSchema
    #from app.schemas.card_assignment_history_schema import LazyCardAssignmentHistoryReadSchema

    id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    email: EmailStr = Field(..., example="jdoe@example.com")
    name: str = Field(..., example="John Doe")
    created_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    cards: List[LazyCardReadSchema] = Field(default_factory=list)
    memberships: List[LazyMembershipReadSchema] = Field(default_factory=list)
    project_permissions: List[LazyIdentityProjectPermissionReadSchema] = Field(default_factory=list)
    #events: List[LazyEventReadSchema] = Field(default_factory=list)
    #card_assignment_history: List[LazyCardAssignmentHistoryReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "email": "jdoe@example.com",
                "name": "John Doe",
                "created_at": "2025-01-01T00:00:00",
                "cards": [],
                "memberships": [],
                "project_permissions": [],
                #"events": [],
                #"card_assignment_history": [],
            }
        },
    )


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
                "name": "John Doe",
            }
        },
    )
