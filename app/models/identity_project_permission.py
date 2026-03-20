import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class IdentityProjectPermission(Base):
    __tablename__ = "identity_project_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    allowed = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    identity = relationship("Identity", back_populates="project_permissions")
    project = relationship("Project", back_populates="permissions")

    __table_args__ = (
        Index("idx_identity_project_permissions_identity_id", "identity_id"),
        Index("idx_identity_project_permissions_project_id", "project_id"),
    )

    def __repr__(self):
        return f"<IdentityProjectPermission(id={self.id}, identity_id={self.identity_id}, project_id={self.project_id}, allowed={self.allowed}, created_at={self.created_at}, updated_at={self.updated_at})>"
