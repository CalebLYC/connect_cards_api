import datetime
import uuid
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean, Index, func
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
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_access_tokens_user_id", "user_id"),
        Index("idx_access_tokens_expires_at", "expires_at"),
    )

    @validates("expires_at")
    def validate_expires_at(self, key, expires_at):
        # Supprime le fuseau horaire si il y en a un
        return (
            expires_at.replace(tzinfo=None)
            if expires_at
            else datetime.datetime.utcnow().replace(tzinfo=None)
        )

    def __repr__(self):
        return f"<AccessToken(id={self.id}, token={self.token}, user_id={self.user_id}, expires_at={self.expires_at}, revoked={self.revoked}, created_at={self.created_at}, updated_at={self.updated_at})>"
