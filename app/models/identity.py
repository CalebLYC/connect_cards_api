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

class Identity(Base):
    __tablename__ = "identities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    cards = relationship("Card", back_populates="identity")
    memberships = relationship("Membership", back_populates="identity")
    project_permissions = relationship(
        "IdentityProjectPermission",
        back_populates="identity"
    )
