"""Internal HTTP session: request dispatch and error mapping."""

from __future__ import annotations

import uuid
from typing import Any

import requests

from .exceptions import AweAuthError, AweError, AweNotFoundError, AweServerError, AweValidationError


def _compact(d: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *d* with all ``None``-valued keys removed."""
    return {k: v for k, v in d.items() if v is not None}


def _str_id(value: Any) -> str | None:
    """Coerce a ``uuid.UUID`` or string identifier to ``str``, pass ``None`` through."""
    if value is None:
        return None
    return str(value) if isinstance(value, uuid.UUID) else value


class _HttpSession:
    """Thin wrapper around :class:`requests.Session` that handles auth headers and
    maps non-2xx responses to typed exceptions."""

    def __init__(self, api_url: str, auth_url: str) -> None:
        self._api_url = api_url.rstrip("/")
        self._auth_url = auth_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._token: str | None = None

    def set_token(self, token: str) -> None:
        """Store the JWT and attach it to all subsequent requests."""
        self._token = token
        self._session.headers["Authorization"] = f"Bearer {token}"

    def _require_auth(self) -> None:
        if self._token is None:
            raise AweAuthError("Not authenticated — call AweClient.login() first.")

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.ok:
            return
        try:
            body = response.json()
            message = body.get("error") or body.get("message") or response.text
        except Exception:
            message = response.text
        if response.status_code == 401:
            raise AweAuthError(message)
        if response.status_code == 403:
            raise AweAuthError(f"Forbidden: {message}")
        if response.status_code == 404:
            raise AweNotFoundError(message)
        if response.status_code == 400:
            raise AweValidationError(message)
        if response.status_code >= 500:
            raise AweServerError(f"Server error {response.status_code}: {message}")
        raise AweError(f"HTTP {response.status_code}: {message}")

    # ── auth service ──────────────────────────────────────────────────────────

    def post_auth(self, path: str, json: Any) -> Any:
        """POST to the authentication service (no JWT header required)."""
        response = self._session.post(f"{self._auth_url}{path}", json=json)
        self._raise_for_status(response)
        return response.json()

    # ── AWE API ───────────────────────────────────────────────────────────────

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        self._require_auth()
        response = self._session.get(f"{self._api_url}{path}", params=params)
        self._raise_for_status(response)
        return response.json()

    def post(self, path: str, json: Any = None) -> Any:
        self._require_auth()
        response = self._session.post(f"{self._api_url}{path}", json=json)
        self._raise_for_status(response)
        return response.json() if response.content else None

    def put(self, path: str, json: Any = None) -> Any:
        self._require_auth()
        response = self._session.put(f"{self._api_url}{path}", json=json)
        self._raise_for_status(response)
        return response.json() if response.content else None

    def patch(self, path: str, json: Any = None) -> Any:
        self._require_auth()
        response = self._session.patch(f"{self._api_url}{path}", json=json)
        self._raise_for_status(response)
        return response.json() if response.content else None

    def delete(self, path: str, json: Any = None) -> Any:
        self._require_auth()
        response = self._session.delete(f"{self._api_url}{path}", json=json)
        self._raise_for_status(response)
        return response.json() if response.content else None
