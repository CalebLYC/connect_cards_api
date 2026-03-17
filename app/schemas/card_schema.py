import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID



class LazyCardReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    uid: str = Field(..., example="CARD123456")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    status: str = Field(..., example="pending")
    activation_code: Optional[str] = Field(default=None, example="123456")
    issuer_organization_id: Optional[UUID] = Field(default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "uid": "CARD123456",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "status": "pending",
                "activation_code": "123456",
                "issuer_organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "created_at": "2025-01-01T00:00:00",
            }
        },
    )


from app.schemas.identity_schema import LazyIdentityReadSchema
from app.schemas.organization_schema import LazyOrganizationReadSchema
class CardReadSchema(BaseModel):
    #from app.schemas.card_assignment_history_schema import LazyCardAssignmentHistoryReadSchema
    
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    uid: str = Field(..., example="CARD123456")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    status: str = Field(..., example="pending")
    activation_code: Optional[str] = Field(default=None, example="123456")
    issuer_organization_id: Optional[UUID] = Field(default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    identity: LazyIdentityReadSchema
    issuer_organization: Optional[LazyOrganizationReadSchema] = Field(default=None)
    #assignment_history: List[LazyCardAssignmentHistoryReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "uid": "CARD123456",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "status": "pending",
                "activation_code": "123456",
                "issuer_organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "created_at": "2025-01-01T00:00:00",
                "identity": {
                    "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "email": "jdoe@example.com",
                    "name": "John Doe",
                    "created_at": "2025-01-01T00:00:00",
                },
                "issuer_organization": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Example Organization",
                    "type": "Company",
                    "created_at": "2025-01-01T00:00:00",
                },
                #"assignment_history": [],
            }
        },
    )


class CardCreateSchema(BaseModel):
    uid: str = Field(..., example="CARD123456")
    identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    status: Optional[str] = Field(default="pending", example="pending")
    activation_code: Optional[str] = Field(default=None, example="123456")
    issuer_organization_id: Optional[UUID] = Field(default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "uid": "CARD123456",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "status": "pending",
                "activation_code": "123456",
                "issuer_organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            }
        },
    )


class CardUpdateSchema(BaseModel):
    uid: Optional[str] = Field(default=None, example="CARD123456")
    identity_id: Optional[UUID] = Field(default=None, example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    status: Optional[str] = Field(default=None, example="active")
    activation_code: Optional[str] = Field(default=None, example="123456")
    issuer_organization_id: Optional[UUID] = Field(default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "uid": "CARD123456",
                "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "status": "active",
                "activation_code": "123456",
                "issuer_organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            }
        },
    )
