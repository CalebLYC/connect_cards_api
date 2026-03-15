import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    card_uid = Column(String)

    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))

    reader_id = Column(UUID(as_uuid=True), ForeignKey("readers.id"))

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))

    result = Column(String)

    created_at = Column(DateTime, server_default=func.now())
