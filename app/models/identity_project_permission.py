import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
   Boolean,
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

    identity = relationship(
        "Identity",
        back_populates="project_permissions"
    )

    project = relationship(
        "Project",
        back_populates="permissions"
    )
