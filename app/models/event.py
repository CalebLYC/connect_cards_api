import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    # Enum as sqlEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.models.base import Base
from app.models.enums.event_type_enum import EventTypeEnum


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"))
    # identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))
    reader_id = Column(UUID(as_uuid=True), ForeignKey("readers.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    # event_type = Column(sqlEnum(EventTypeEnum))
    event_type = Column(String(50), nullable=True)
    metadata_desc = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    card = relationship("Card", back_populates="events")
    # identity = relationship("Identity", back_populates="events")
    reader = relationship("Reader", back_populates="events")
    project = relationship("Project", back_populates="events")
    __table_args__ = (
        Index("idx_events_card_id", "card_id"),
        Index("idx_events_reader_id", "reader_id"),
        Index("idx_events_project_id", "project_id"),
        Index("idx_events_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, card_id={self.card_id}, reader_id={self.reader_id}, project_id={self.project_id}, event_type={self.event_type}, created_at={self.created_at})>"
