from enum import Enum
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Enum as SqlEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class OrganizationTypeEnum(str, Enum):
    COMPANY = "Company"
    NON_PROFIT = "Non-Profit"
    GOVERNMENT = "Government"
    OTHER = "Other"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(SqlEnum(OrganizationTypeEnum), default=OrganizationTypeEnum.COMPANY.value)
    created_at = Column(DateTime, server_default=func.now())

    memberships = relationship("Membership", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    readers = relationship("Reader", back_populates="organization")
    users = relationship("User", back_populates="organization")
    issued_cards = relationship("Card", back_populates="issuer_organization")
