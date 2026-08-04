# ============================
# User Roles
# ============================

ROLE_CITIZEN = "Citizen"
ROLE_FAMILY = "Family"
ROLE_RESPONDER = "Responder"
ROLE_HOSPITAL = "Hospital"
ROLE_POLICE = "Police"
ROLE_ADMIN = "Admin"

ROLES = [
    ROLE_CITIZEN,
    ROLE_FAMILY,
    ROLE_RESPONDER,
    ROLE_HOSPITAL,
    ROLE_POLICE,
    ROLE_ADMIN,
]

# ============================
# Account Status
# ============================

ACTIVE = True
INACTIVE = False

VERIFIED = True
UNVERIFIED = False

# ============================
# Messages
# ============================

USER_CREATED = "User registered successfully."
LOGIN_SUCCESS = "Login successful."
INVALID_CREDENTIALS = "Invalid email or password."
EMAIL_EXISTS = "Email already registered."
INVALID_ROLE = "Invalid role."
UNAUTHORIZED = "Unauthorized."