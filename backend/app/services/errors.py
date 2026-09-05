"""Service-layer exceptions, translated to HTTP status codes in app.api."""
from __future__ import annotations


class ServiceError(Exception):
    """Base class for expected, client-facing service failures."""


class NotFoundError(ServiceError):
    pass


class DomainValidationError(ServiceError):
    pass
