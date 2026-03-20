from enum import Enum


class OrganizationTypeEnum(str, Enum):
    COMPANY = "Company"
    NON_PROFIT = "Non-Profit"
    GOVERNMENT = "Government"
    OTHER = "Other"
