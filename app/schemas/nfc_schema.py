from pydantic import BaseModel, ConfigDict, Field
from typing import List
from uuid import UUID

from app.schemas.identity_schema import LazyIdentityReadSchema
from app.schemas.card_schema import LazyCardReadSchema


class ScanCardResponse(BaseModel):
    authorized: bool = Field(..., description="Whether the card access is authorized")
    user: LazyIdentityReadSchema = Field(
        ..., description="The user associated with the card"
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="List of permissions or roles for the user in the project organization",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "authorized": True,
                "user": {
                    "id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "name": "John Doe",
                    "email": "jdoe@gmail.com",
                },
                "permissions": ["admin", "editor"],
            }
        },
    )


class CardActivationRequest(BaseModel):
    card_uid: str = Field(..., description="The physical UID of the NFC card")
    activation_code: str = Field(..., description="The unique activation code")
    identity_id: UUID = Field(
        ..., description="The ID of the identity (user) to link the card to"
    )


class CardActivationResponse(BaseModel):
    success: bool = Field(..., description="Whether the activation was successful")
    card: LazyCardReadSchema = Field(..., description="The activated card")
