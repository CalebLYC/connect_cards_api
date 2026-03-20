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


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="projects")
    permissions = relationship("IdentityProjectPermission", back_populates="project")
    events = relationship("Event", back_populates="project")
    readers = relationship("Reader", back_populates="project")

    __table_args__ = (Index("idx_projects_organization_id", "organization_id"),)

    def __repr__(self):
        return f"<Project(id={self.id}, organization_id={self.organization_id}, name={self.name}, description={self.description}, created_at={self.created_at}, updated_at={self.updated_at})>"
