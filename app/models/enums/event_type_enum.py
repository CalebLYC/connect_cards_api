from enum import Enum


class EventTypeEnum(str, Enum):
    ACCESS_DENIED = "access_denied"
    ACCESS_GRANTED = "access_granted"
    CARD_ASSIGNED = "card_assigned"
    CARD_UNASSIGNED = "card_unassigned"
    CARD_ACTIVATED = "card_activated"
    CARD_DEACTIVATED = "card_deactivated"
    CARD_ISSUED = "card_issued"
    CARD_REVOKED = "card_revoked"
    CARD_LOST = "card_lost"
    CARD_FOUND = "card_found"
    CARD_STOLEN = "card_stolen"
    CARD_RECOVERED = "card_recovered"
    CARD_EXPIRED = "card_expired"
    CARD_DAMAGED = "card_damaged"
    CARD_UNKNOWN = "card_unknown"
