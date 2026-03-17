import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"))
    #identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))
    reader_id = Column(UUID(as_uuid=True), ForeignKey("readers.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    result = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    card = relationship("Card", back_populates="events")
    #identity = relationship("Identity", back_populates="events")
    reader = relationship("Reader", back_populates="events")
    project = relationship("Project", back_populates="events")
    __table_args__ = (
        Index("idx_events_card_id", "card_id"),
        Index("idx_events_reader_id", "reader_id"),
        Index("idx_events_project_id", "project_id"),
        Index("idx_events_created_at", "created_at"),
    )