import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Reader(Base):
    __tablename__ = "readers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id")
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )
    name = Column(String)
    location = Column(String)
    status = Column(String, default="active")

    organization = relationship("Organization", back_populates="readers")
    project = relationship("Project", back_populates="readers")
