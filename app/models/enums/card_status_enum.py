from enum import Enum


class CardStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    BLOCKED = "blocked"
    LOST = "lost"
    STOLEN = "stolen"
    DAMAGED = "damaged"
