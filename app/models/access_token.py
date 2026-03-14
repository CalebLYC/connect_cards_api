import datetime
import uuid
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.models.base import Base


class AccessToken(Base):
    __tablename__ = "access_tokens"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    token = Column(String(255), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="access_tokens")
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @validates("expires_at")
    def validate_expires_at(self, key, expires_at):
        # Supprime le fuseau horaire si il y en a un
        return (
            expires_at.replace(tzinfo=None)
            if expires_at
            else datetime.datetime.utcnow().replace(tzinfo=None)
        )
