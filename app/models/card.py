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


class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uid = Column(String, unique=True, nullable=False)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"), nullable=True)
    status = Column(String, default="pending")
    activation_code = Column(String, nullable=True)
    issuer_organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    identity = relationship("Identity", back_populates="cards")
    issuer_organization = relationship("Organization", back_populates="issued_cards")
    assignment_history = relationship("CardAssignmentHistory", back_populates="card")
    events = relationship("Event", back_populates="card")

    __table_args__ = (
        Index("idx_cards_uid", "uid"),
        Index("idx_cards_identity_id", "identity_id"),
        Index("idx_cards_issuer_organization_id", "issuer_organization_id"),
    )

    def __repr__(self):
        return f"<Card(id={self.id}, uid={self.uid}, identity_id={self.identity_id}, status={self.status}, activation_code={self.activation_code}, issuer_organization_id={self.issuer_organization_id}, created_at={self.created_at}, updated_at={self.updated_at})>"
