import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
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
    
    card = relationship("Card", back_populates="assignment_history")
    identity = relationship("Identity", back_populates="card_assignment_history")
