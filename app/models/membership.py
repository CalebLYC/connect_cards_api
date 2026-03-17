
import uuid
from sqlalchemy import (
    ARRAY,
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

class Membership(Base):
    __tablename__ = "memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    roles = Column(ARRAY(String))
    status = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())

    identity = relationship("Identity", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")

    __table_args__ = (
        Index("idx_memberships_identity_id", "identity_id"),
        Index("idx_memberships_organization_id", "organization_id"),
    )
