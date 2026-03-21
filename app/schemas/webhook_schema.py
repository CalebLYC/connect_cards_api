from typing import Optional
from pydantic import BaseModel, ConfigDict, HttpUrl
import uuid
import datetime


class WebhookBaseSchema(BaseModel):
    url: str
    event_type: str
    organization_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    is_active: bool = True
    secret: Optional[str] = None


class WebhookCreateSchema(WebhookBaseSchema):
    pass


class WebhookUpdateSchema(BaseModel):
    url: Optional[str] = None
    event_type: Optional[str] = None
    organization_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None
    secret: Optional[str] = None


class WebhookReadSchema(WebhookBaseSchema):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
