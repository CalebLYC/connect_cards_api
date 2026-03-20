import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID


class LazyReaderReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: Optional[str] = Field(default=None, example="Reader 1")
    location: Optional[str] = Field(default=None, example="Entrance")
    status: str = Field(..., example="active")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Reader 1",
                "location": "Entrance",
                "status": "active",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


class ReaderCreateSchema(BaseModel):
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: Optional[str] = Field(default=None, example="Reader 1")
    location: Optional[str] = Field(default=None, example="Entrance")
    status: Optional[str] = Field(default="active", example="active")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Reader 1",
                "location": "Entrance",
                "status": "active",
            }
        },
    )


class ReaderUpdateSchema(BaseModel):
    organization_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    project_id: Optional[UUID] = Field(
        default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851"
    )
    name: Optional[str] = Field(default=None, example="Updated Reader")
    location: Optional[str] = Field(default=None, example="Exit")
    status: Optional[str] = Field(default=None, example="inactive")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Updated Reader",
                "location": "Exit",
                "status": "inactive",
            }
        },
    )


from app.schemas.organization_schema import LazyOrganizationReadSchema
from app.schemas.project_schema import LazyProjectReadSchema


class ReaderReadSchema(BaseModel):
    # from app.schemas.event_schema import LazyEventReadSchema

    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    project_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: Optional[str] = Field(default=None, example="Reader 1")
    location: Optional[str] = Field(default=None, example="Entrance")
    status: str = Field(..., example="active")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    updated_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    organization: LazyOrganizationReadSchema
    project: LazyProjectReadSchema
    # events: List[LazyEventReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "project_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Reader 1",
                "location": "Entrance",
                "status": "active",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "organization": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Example Organization",
                    "type": "Company",
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
                # "events": [],
            }
        },
    )
