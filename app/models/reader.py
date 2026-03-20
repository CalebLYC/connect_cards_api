import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Reader(Base):
    __tablename__ = "readers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name = Column(String)
    location = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="readers")
    project = relationship("Project", back_populates="readers")
    events = relationship("Event", back_populates="reader")

    __table_args__ = (
        UniqueConstraint("name", "organization_id", name="uq_reader_name_org_id"),
        Index("idx_readers_organization_id", "organization_id"),
        Index("idx_readers_project_id", "project_id"),
    )

    def __repr__(self):
        return f"<Reader(id={self.id}, organization_id={self.organization_id}, project_id={self.project_id}, name={self.name}, location={self.location}, status={self.status})>"
