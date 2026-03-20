import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class LazyCardAssignmentHistoryReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    card_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    assigned_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    unassigned_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-02T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "assigned_at": "2025-01-01T00:00:00",
                "unassigned_at": "2025-01-02T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


class CardAssignmentHistoryCreateSchema(BaseModel):
    card_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    assigned_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    unassigned_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-02T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "assigned_at": "2025-01-01T00:00:00",
                "unassigned_at": "2025-01-02T00:00:00",
            }
        },
    )


class CardAssignmentHistoryUpdateSchema(BaseModel):
    card_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    identity_id: Optional[UUID] = Field(
        default=None, example="04bcf3f5-cde5-4d27-8a20-2f50076043c5"
    )
    assigned_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )
    unassigned_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-02T00:00:00"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "assigned_at": "2025-01-01T00:00:00",
                "unassigned_at": "2025-01-02T00:00:00",
            }
        },
    )


from app.schemas.card_schema import LazyCardReadSchema
from app.schemas.identity_schema import LazyIdentityReadSchema


class CardAssignmentHistoryReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    card_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    assigned_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    unassigned_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-02T00:00:00"
    )
    card: LazyCardReadSchema
    identity: LazyIdentityReadSchema

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "assigned_at": "2025-01-01T00:00:00",
                "unassigned_at": "2025-01-02T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "card": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "uid": "CARD123456",
                    "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "status": "active",
                    "activation_code": "123456",
                    "issuer_organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
                "identity": {
                    "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "email": "jdoe@example.com",
                    "name": "John Doe",
                    "sex": "M",
                    "phone": "+2250707070707",
                    "address": "123 Rue de la Paix",
                    "date_of_birth": "1990-01-01T00:00:00",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
            }
        },
    )
