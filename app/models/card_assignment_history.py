import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class CardAssignmentHistory(Base):
    __tablename__ = "card_assignment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"))
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))
    assigned_at = Column(DateTime, server_default=func.now())
    unassigned_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    card = relationship("Card", back_populates="assignment_history")
    identity = relationship("Identity", back_populates="card_assignment_history")

    __table_args__ = (
        Index("idx_card_assignment_history_card_id", "card_id"),
        Index("idx_card_assignment_history_identity_id", "identity_id"),
        Index("idx_card_assignment_history_assigned_at", "assigned_at"),
        Index("idx_card_assignment_history_unassigned_at", "unassigned_at"),
    )

    def __repr__(self):
        return f"<CardAssignmentHistory(id={self.id}, card_id={self.card_id}, identity_id={self.identity_id}, assigned_at={self.assigned_at}, unassigned_at={self.unassigned_at}, updated_at={self.updated_at})>"
