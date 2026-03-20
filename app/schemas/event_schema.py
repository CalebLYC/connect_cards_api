import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class LazyEventReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    card_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    # identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    reader_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    result: str = Field(..., example="granted")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    description: Optional[str] = Field(default=None, example="Event description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "result": "granted",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "description": "Event description",
            }
        },
    )


class EventCreateSchema(BaseModel):
    card_id: Optional[UUID] = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    # identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    reader_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    result: str = Field(..., example="granted")
    description: Optional[str] = Field(default=None, example="Event description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "result": "granted",
                "description": "Event description",
            }
        },
    )


class EventUpdateSchema(BaseModel):
    card_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    # identity_id: Optional[UUID] = Field(default=None, example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    reader_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    result: Optional[str] = Field(default=None, example="denied")
    description: Optional[str] = Field(
        default=None, example="Updated event description"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                # "card_uid": "CARD123456",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "result": "denied",
                "description": "Updated event description",
            }
        },
    )


from app.schemas.card_schema import LazyCardReadSchema
from app.schemas.reader_schema import LazyReaderReadSchema
from app.schemas.project_schema import LazyProjectReadSchema


class EventReadSchema(BaseModel):
    # from app.schemas.identity_schema import LazyIdentityReadSchema

    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    card_id: Optional[UUID] = Field(example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    # identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    reader_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    result: str = Field(..., example="granted")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    description: Optional[str] = Field(default=None, example="Event description")
    # identity: LazyIdentityReadSchema
    card: LazyCardReadSchema
    reader: Optional[LazyReaderReadSchema] = Field(default=None)
    project: LazyProjectReadSchema

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "result": "granted",
                "description": "Event description",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "card": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "uid": "CARD123456",
                    "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                    "status": "pending",
                    "activation_code": "123456",
                    "issuer_organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
                "reader": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Reader 1",
                    "location": "Entrance",
                    "status": "active",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
                "project": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Example Project",
                    "description": "A sample project description",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
            }
        },
    )
