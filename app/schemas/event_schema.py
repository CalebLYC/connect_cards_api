import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID

from app.models.enums.event_type_enum import EventTypeEnum


class LazyEventReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    card_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    # identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    reader_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    event_type: EventTypeEnum = Field(..., example="granted")
    metadata_desc: Optional[dict] = Field(default=None, example="Event description")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    """updated_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "event_type": "granted",
                "metadata_desc": {
                    "result": "granted",
                    "description": "Event description",
                },
                "created_at": "2025-01-01T00:00:00",
                # "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


class EventCreateSchema(BaseModel):
    card_id: Optional[UUID] = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    # identity_id: UUID = Field(..., example="04bcf3f5-cde5-4d27-8a20-2f50076043c5")
    reader_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    event_type: EventTypeEnum = Field(..., example="granted")
    metadata_desc: Optional[dict] = Field(default=None, example="Event description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "event_type": "granted",
                "metadata_desc": {
                    "result": "granted",
                    "description": "Event description",
                },
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
    event_type: Optional[EventTypeEnum] = Field(default=None, example="denied")
    metadata_desc: Optional[dict] = Field(default=None, example="Event description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                # "card_uid": "CARD123456",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "event_type": "denied",
                "metadata_desc": {
                    "result": "denied",
                    "description": "Event description",
                },
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
    project_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    event_type: EventTypeEnum = Field(..., example="granted")
    metadata_desc: Optional[dict] = Field(default=None, example="Event description")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    """updated_at: Optional[datetime.datetime] = Field(
        default=None, example="2025-01-01T00:00:00"
    )"""
    # identity: LazyIdentityReadSchema
    card: Optional[LazyCardReadSchema] = Field(default=None)
    reader: Optional[LazyReaderReadSchema] = Field(default=None)
    project: Optional[LazyProjectReadSchema] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "card_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                # "identity_id": "04bcf3f5-cde5-4d27-8a20-2f50076043c5",
                "reader_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "event_type": "granted",
                "metadata_desc": {
                    "result": "granted",
                    "description": "Event description",
                },
                "created_at": "2025-01-01T00:00:00",
                # "updated_at": "2025-01-01T00:00:00",
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
