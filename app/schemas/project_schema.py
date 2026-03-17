import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID



class LazyProjectReadSchema(BaseModel):
    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: str = Field(..., example="Example Project")
    description: Optional[str] = Field(default=None, example="A sample project description")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Example Project",
                "description": "A sample project description",
                "created_at": "2025-01-01T00:00:00",
            }
        },
    )

    
class ProjectCreateSchema(BaseModel):
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: str = Field(..., example="Example Project")
    description: Optional[str] = Field(default=None, example="A sample project description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Example Project",
                "description": "A sample project description",
            }
        },
    )


class ProjectUpdateSchema(BaseModel):
    organization_id: Optional[UUID] = Field(default=None, example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: Optional[str] = Field(default=None, example="Updated Project")
    description: Optional[str] = Field(default=None, example="Updated description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Updated Project",
                "description": "Updated description",
            }
        },
    )


from app.schemas.organization_schema import LazyOrganizationReadSchema
from app.schemas.identity_project_permission_schema import LazyIdentityProjectPermissionReadSchema
from app.schemas.reader_schema import LazyReaderReadSchema
class ProjectReadSchema(BaseModel):
    #from app.schemas.event_schema import LazyEventReadSchema

    id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    organization_id: UUID = Field(..., example="d290f1ee-6c54-4b01-90e6-d701748f0851")
    name: str = Field(..., example="Example Project")
    description: Optional[str] = Field(default=None, example="A sample project description")
    created_at: datetime.datetime = Field(..., example="2025-01-01T00:00:00")
    organization: LazyOrganizationReadSchema
    permissions: List[LazyIdentityProjectPermissionReadSchema] = Field(default_factory=list)
    readers: List[LazyReaderReadSchema] = Field(default_factory=list)
    #events: List[LazyEventReadSchema] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "organization_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Example Project",
                "description": "A sample project description",
                "created_at": "2025-01-01T00:00:00",
                "organization": {
                    "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "name": "Example Organization",
                    "type": "Company",
                    "created_at": "2025-01-01T00:00:00",
                },
                "permissions": [],
                "readers": [],
                #"events": [],
            }
        },
    )
