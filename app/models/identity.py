import uuid
from sqlalchemy import (
    Column,
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Enum as SqlEnum

from app.models.base import Base
from app.models.enums.sex_enum import SexEnum


class Identity(Base):
    __tablename__ = "identities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    sex = Column(SqlEnum(SexEnum), nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cards = relationship("Card", back_populates="identity")
    memberships = relationship("Membership", back_populates="identity")
    project_permissions = relationship(
        "IdentityProjectPermission", back_populates="identity"
    )
    # events = relationship("Event", back_populates="identity")
    card_assignment_history = relationship(
        "CardAssignmentHistory", back_populates="identity"
    )

    def __repr__(self):
        return f"<Identity(id={self.id}, name={self.name}, email={self.email})>"
