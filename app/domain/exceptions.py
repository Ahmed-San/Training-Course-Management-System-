class AppException(Exception):
    """Base exception for predictable application-level failures."""


class ValidationError(AppException):
    """Input or domain invariant validation failed."""


class AuthenticationError(AppException):
    """Credentials or authentication state are invalid."""


class AuthorizationError(AppException):
    """The authenticated user lacks permission for an operation."""


class NotFoundError(AppException):
    """Requested entity does not exist."""


class DuplicateError(AppException):
    """An operation would create a duplicate unique identity."""


class BusinessRuleError(AppException):
    """A validly shaped request violates a business rule."""


class StorageError(AppException):
    """Persistence or serialization failed."""
