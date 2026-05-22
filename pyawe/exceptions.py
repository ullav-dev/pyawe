"""Exceptions raised by the pyawe client."""

from __future__ import annotations


class AweError(Exception):
    """Base class for all pyawe exceptions."""


class AweAuthError(AweError):
    """Raised on 401 responses or when :meth:`AweClient.login` has not been called."""


class AweNotFoundError(AweError):
    """Raised on 404 responses."""


class AweValidationError(AweError):
    """Raised on 400 responses."""


class AweServerError(AweError):
    """Raised on 5xx responses."""
