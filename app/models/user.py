import datetime
import uuid
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SqlEnum,
    String,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class SexEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"


# Table d'association User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
)

# Table d'association User <-> Permission
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    sex = Column(SqlEnum(SexEnum), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    picture = Column(String(255), nullable=True)
    locale = Column(String(20), nullable=True)
    birthday_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)

    roles = relationship("Role", secondary=user_roles, backref="users")
    permissions = relationship("Permission", secondary=user_permissions, backref="users")
    organization = relationship("Organization", back_populates="users")

    def has_role(self, role_name: str) -> bool:
        """Vérifie si l'utilisateur possède un rôle donné."""
        return any(role.name == role_name for role in self.roles)

    def get_roles(self) -> list:
        """Retourne la liste des noms de rôles de l'utilisateur."""
        return [role.name for role in self.roles]
    
    def has_permission(self, permission_code: str) -> bool:
        """Vérifie si l'utilisateur possède une permission donnée."""
        return any(p_code == permission_code for p_code in self.get_all_permissions())

    def get_permissions(self) -> list:
        """Retourne la liste des noms de permissions de l'utilisateur."""
        return [permission.code for permission in self.permissions]
    
    def get_all_permissions(self) -> list:
        """Retourne la liste des noms de permissions de l'utilisateur."""
        return [permission.code for permission in [perm for role in self.roles for perm in role.permissions] + self.permissions]


    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
