"""Tests for _HttpSession, _compact, and _str_id."""

from __future__ import annotations

import json
import uuid

import pytest
import responses as rsps_lib

from pyawe._http import _HttpSession, _compact, _str_id
from pyawe.exceptions import (
    AweAuthError,
    AweError,
    AweNotFoundError,
    AweServerError,
    AweValidationError,
)

API = "http://test-api"
AUTH = "http://test-auth"


def make_session() -> _HttpSession:
    return _HttpSession(API, AUTH)


def authed_session() -> _HttpSession:
    s = make_session()
    s.set_token("tok")
    return s


# ── _compact ──────────────────────────────────────────────────────────────────


def test_compact_removes_none_values():
    assert _compact({"a": None, "b": 1}) == {"b": 1}


def test_compact_keeps_falsy_non_none():
    result = _compact({"a": 0, "b": False, "c": "", "d": []})
    assert result == {"a": 0, "b": False, "c": "", "d": []}


def test_compact_empty_dict():
    assert _compact({}) == {}


def test_compact_all_none_returns_empty():
    assert _compact({"a": None, "b": None}) == {}


def test_compact_does_not_mutate_input():
    original = {"a": None, "b": 1}
    _compact(original)
    assert original == {"a": None, "b": 1}


# ── _str_id ───────────────────────────────────────────────────────────────────


def test_str_id_converts_uuid_to_str():
    uid = uuid.UUID("11111111-1111-1111-1111-111111111111")
    result = _str_id(uid)
    assert result == "11111111-1111-1111-1111-111111111111"
    assert isinstance(result, str)


def test_str_id_passes_string_through():
    assert _str_id("some-id") == "some-id"


def test_str_id_none_returns_none():
    assert _str_id(None) is None


# ── _HttpSession initialisation ───────────────────────────────────────────────


def test_trailing_slash_stripped_from_api_url():
    session = _HttpSession(f"{API}/", AUTH)
    assert session._api_url == API


def test_trailing_slash_stripped_from_auth_url():
    session = _HttpSession(API, f"{AUTH}/")
    assert session._auth_url == AUTH


# ── authentication ────────────────────────────────────────────────────────────


def test_require_auth_raises_when_no_token():
    session = make_session()
    with pytest.raises(AweAuthError, match="login"):
        session._require_auth()


def test_require_auth_passes_after_set_token():
    session = make_session()
    session.set_token("tok")
    session._require_auth()  # must not raise


def test_set_token_attaches_bearer_header():
    session = make_session()
    session.set_token("mytoken")
    assert session._session.headers["Authorization"] == "Bearer mytoken"


def test_set_token_replaces_previous_token():
    session = make_session()
    session.set_token("first")
    session.set_token("second")
    assert session._session.headers["Authorization"] == "Bearer second"


@rsps_lib.activate
def test_get_raises_auth_error_without_token():
    session = make_session()
    with pytest.raises(AweAuthError):
        session.get("/workflows")


@rsps_lib.activate
def test_post_raises_auth_error_without_token():
    session = make_session()
    with pytest.raises(AweAuthError):
        session.post("/workflows")


@rsps_lib.activate
def test_put_raises_auth_error_without_token():
    session = make_session()
    with pytest.raises(AweAuthError):
        session.put("/workflows/x")


@rsps_lib.activate
def test_patch_raises_auth_error_without_token():
    session = make_session()
    with pytest.raises(AweAuthError):
        session.patch("/workflows/x")


@rsps_lib.activate
def test_delete_raises_auth_error_without_token():
    session = make_session()
    with pytest.raises(AweAuthError):
        session.delete("/workflows/x")


@rsps_lib.activate
def test_post_auth_does_not_require_token():
    """post_auth is for the auth service — no JWT needed."""
    session = make_session()
    rsps_lib.add(rsps_lib.POST, f"{AUTH}/auth/login", json={"token": "t"})
    result = session.post_auth("/auth/login", {"email": "a", "password": "b"})
    assert result == {"token": "t"}


# ── error mapping ─────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_400_raises_validation_error():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "bad input"}, status=400)
    with pytest.raises(AweValidationError, match="bad input"):
        session.get("/x")


@rsps_lib.activate
def test_401_raises_auth_error():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "Unauthorized"}, status=401)
    with pytest.raises(AweAuthError):
        session.get("/x")


@rsps_lib.activate
def test_403_raises_auth_error_with_forbidden_prefix():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "nope"}, status=403)
    with pytest.raises(AweAuthError, match="Forbidden"):
        session.get("/x")


@rsps_lib.activate
def test_404_raises_not_found():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "not found"}, status=404)
    with pytest.raises(AweNotFoundError):
        session.get("/x")


@rsps_lib.activate
def test_500_raises_server_error():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "boom"}, status=500)
    with pytest.raises(AweServerError, match="500"):
        session.get("/x")


@rsps_lib.activate
def test_502_raises_server_error():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "gateway"}, status=502)
    with pytest.raises(AweServerError):
        session.get("/x")


@rsps_lib.activate
def test_409_raises_generic_awe_error():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"error": "conflict"}, status=409)
    with pytest.raises(AweError):
        session.get("/x")


@rsps_lib.activate
def test_error_body_message_key_used_as_fallback():
    """Auth service uses 'message' rather than 'error'."""
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"message": "auth svc msg"}, status=401)
    with pytest.raises(AweAuthError, match="auth svc msg"):
        session.get("/x")


@rsps_lib.activate
def test_error_body_with_neither_key_falls_back_to_text():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/x", json={"detail": "something"}, status=400)
    with pytest.raises(AweValidationError):
        session.get("/x")


@rsps_lib.activate
def test_non_json_error_body_falls_back_to_text():
    session = authed_session()
    rsps_lib.add(
        rsps_lib.GET, f"{API}/x",
        body=b"Internal Server Error",
        status=500,
        content_type="text/plain",
    )
    with pytest.raises(AweServerError, match="Internal Server Error"):
        session.get("/x")


# ── 204 No Content ────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_post_204_returns_none():
    session = authed_session()
    rsps_lib.add(rsps_lib.POST, f"{API}/x", status=204)
    assert session.post("/x") is None


@rsps_lib.activate
def test_put_204_returns_none():
    session = authed_session()
    rsps_lib.add(rsps_lib.PUT, f"{API}/x", status=204)
    assert session.put("/x") is None


@rsps_lib.activate
def test_patch_204_returns_none():
    session = authed_session()
    rsps_lib.add(rsps_lib.PATCH, f"{API}/x", status=204)
    assert session.patch("/x") is None


@rsps_lib.activate
def test_delete_204_returns_none():
    session = authed_session()
    rsps_lib.add(rsps_lib.DELETE, f"{API}/x", status=204)
    assert session.delete("/x") is None


# ── request mechanics ─────────────────────────────────────────────────────────


@rsps_lib.activate
def test_get_sends_query_params():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/items", json=[])
    session.get("/items", params={"team_id": "abc"})
    assert "team_id=abc" in rsps_lib.calls[0].request.url


@rsps_lib.activate
def test_post_sends_json_body():
    session = authed_session()
    rsps_lib.add(rsps_lib.POST, f"{API}/items", json={"id": "x"})
    session.post("/items", json={"name": "test"})
    body = json.loads(rsps_lib.calls[0].request.body)
    assert body == {"name": "test"}


@rsps_lib.activate
def test_put_sends_json_body():
    session = authed_session()
    rsps_lib.add(rsps_lib.PUT, f"{API}/items/x", json={"id": "x"})
    session.put("/items/x", json={"name": "updated"})
    body = json.loads(rsps_lib.calls[0].request.body)
    assert body == {"name": "updated"}


@rsps_lib.activate
def test_patch_sends_json_body():
    session = authed_session()
    rsps_lib.add(rsps_lib.PATCH, f"{API}/items/x", json={"id": "x"})
    session.patch("/items/x", json={"value": 42})
    body = json.loads(rsps_lib.calls[0].request.body)
    assert body == {"value": 42}


@rsps_lib.activate
def test_all_api_requests_send_bearer_header():
    session = authed_session()
    rsps_lib.add(rsps_lib.GET, f"{API}/items", json=[])
    session.get("/items")
    assert rsps_lib.calls[0].request.headers["Authorization"] == "Bearer tok"


@rsps_lib.activate
def test_api_url_double_slash_avoided():
    """Trailing slash on api_url must be stripped so paths don't get //."""
    session = _HttpSession(f"{API}/", AUTH)
    session.set_token("tok")
    rsps_lib.add(rsps_lib.GET, f"{API}/workflows", json=[])
    session.get("/workflows")
    assert rsps_lib.calls[0].request.url == f"{API}/workflows"
