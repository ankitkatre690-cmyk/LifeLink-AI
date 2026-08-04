class AuthenticationError(Exception):
    """Base authentication exception."""


class EmailAlreadyExistsError(AuthenticationError):
    """Email already exists."""


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password."""


class InvalidRoleError(AuthenticationError):
    """Invalid role selected."""


class UserNotFoundError(AuthenticationError):
    """User not found."""