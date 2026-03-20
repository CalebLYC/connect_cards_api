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
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship
import datetime

from app.models.base import Base


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    roles = Column(ARRAY(String))
    status = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    identity = relationship("Identity", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint(
            "identity_id", "organization_id", name="uq_membership_identity_org"
        ),
        Index("idx_memberships_identity_id", "identity_id"),
        Index("idx_memberships_organization_id", "organization_id"),
    )

    def __repr__(self):
        return f"<Membership(id={self.id}, identity_id={self.identity_id}, organization_id={self.organization_id}, roles={self.roles}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})>"
