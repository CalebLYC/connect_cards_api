import uuid
from sqlalchemy import (
    Column,
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    type = Column(String)

    created_at = Column(DateTime, server_default=func.now())

    memberships = relationship("Membership", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    readers = relationship("Reader", back_populates="organization")
    users = relationship("User", back_populates="organization")
