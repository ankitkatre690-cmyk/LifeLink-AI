from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "Citizen"
    FAMILY = "Family"
    RESPONDER = "Responder"
    HOSPITAL = "Hospital"
    POLICE = "Police"
    ADMIN = "Admin"