import datetime
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

# Table d'association Role <-> Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    permissions = relationship(
        "Permission", secondary=role_permissions, backref="roles"
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, description={self.description}, created_at={self.created_at}, updated_at={self.updated_at})>"
