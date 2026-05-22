# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

`pyawe` is a Python client library for the **AWE (Advanced Workflow Engine)** API, backed by `awe-server` (Rust/Axum, PostgreSQL) in the Ullav monorepo at `../awe-server`. Authentication is delegated to `ullav-user-management` at `../ullav-user-management`. See `../CLAUDE.md` for the broader ecosystem context.

## Links

- **PyPI**: https://pypi.org/project/pyawe/
- **Docs**: https://ullav-dev.github.io/pyawe/

## Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint / format
ruff check pyawe
ruff format pyawe

# Type-check
mypy pyawe

# Build for PyPI
python -m build

# Preview docs locally
pip install -e ".[docs]"
mkdocs serve
```

## Package structure

```
pyawe/
  __init__.py          # public surface: AweClient, all exceptions, all models/enums
  client.py            # AweClient + twelve resource sub-client classes
  models.py            # dataclasses mirroring the Rust API schemas
  exceptions.py        # AweError, AweAuthError, AweNotFoundError, AweValidationError, AweServerError
  _http.py             # _HttpSession: requests.Session wrapper, error mapping, _compact/_str_id helpers
```

## Architecture

`AweClient.__init__` instantiates twelve sub-clients (one per resource family) and passes them the same `_HttpSession` instance. All state — the JWT token — lives in `_HttpSession`. Call `AweClient.login(email, password)` before any resource method; the token is stored on the session and sent automatically as `Authorization: Bearer <token>`.

Authentication calls `POST <auth_url>/auth/login` on the `ullav-user-management` service. All AWE API calls go to `<api_url>`. The two URLs are separate; `auth_url` defaults to `api_url` when both are behind the same proxy.

### Key design patterns

- **`_compact(d)`** strips `None` values before sending request bodies (server uses COALESCE — omitting a field leaves it unchanged).
- **`assigned_to` tri-state** — uses a module-level `_UNSET` sentinel in `client.py`. Passing `assigned_to=None` sends `null` (clears the assignment); omitting it entirely leaves the field untouched.
- **Enums are `str` subclasses** — `Status("In Progress")` round-trips through JSON without custom serialisers. The wire values have spaces and mixed case; don't use `.value` explicitly.
- **`from_dict` classmethods** parse UUIDs (`uuid.UUID`) and datetimes (`datetime.fromisoformat`, with `Z → +00:00` normalisation) from the raw JSON dicts returned by `_HttpSession`.

### Error mapping

`_HttpSession._raise_for_status` checks for `{"error": "..."}` in the response body (AWE server format). The auth service may return `{"message": "..."}` so both keys are checked.
