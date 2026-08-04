class AppException(Exception):
    """Base application exception."""


class BadRequestException(AppException):
    """400 Bad Request."""


class UnauthorizedException(AppException):
    """401 Unauthorized."""


class ForbiddenException(AppException):
    """403 Forbidden."""


class NotFoundException(AppException):
    """404 Resource Not Found."""


class ConflictException(AppException):
    """409 Conflict."""


class ValidationException(AppException):
    """422 Validation Error."""