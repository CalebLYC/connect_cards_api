import datetime
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code}, description={self.description}, created_at={self.created_at}, updated_at={self.updated_at})>"
