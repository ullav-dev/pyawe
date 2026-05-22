"""Tests for the pyawe exception hierarchy."""

from __future__ import annotations

import pytest

from pyawe.exceptions import (
    AweAuthError,
    AweError,
    AweNotFoundError,
    AweServerError,
    AweValidationError,
)


def test_all_exceptions_subclass_awe_error():
    assert issubclass(AweAuthError, AweError)
    assert issubclass(AweNotFoundError, AweError)
    assert issubclass(AweValidationError, AweError)
    assert issubclass(AweServerError, AweError)


def test_awe_error_subclasses_exception():
    assert issubclass(AweError, Exception)


def test_exceptions_carry_message():
    for cls in (AweError, AweAuthError, AweNotFoundError, AweValidationError, AweServerError):
        exc = cls("test message")
        assert str(exc) == "test message"


def test_auth_error_catchable_as_base():
    with pytest.raises(AweError):
        raise AweAuthError("nope")


def test_not_found_catchable_as_base():
    with pytest.raises(AweError):
        raise AweNotFoundError("gone")


def test_validation_error_catchable_as_base():
    with pytest.raises(AweError):
        raise AweValidationError("bad")


def test_server_error_catchable_as_base():
    with pytest.raises(AweError):
        raise AweServerError("boom")


def test_distinct_subclasses_not_interchangeable():
    with pytest.raises(AweAuthError):
        raise AweAuthError("auth")
    with pytest.raises(AweNotFoundError):
        raise AweNotFoundError("404")
    # AweAuthError does NOT catch AweNotFoundError
    with pytest.raises(Exception):
        try:
            raise AweNotFoundError("404")
        except AweAuthError:
            pass
        else:
            raise Exception("caught wrong type")  # noqa: TRY301
