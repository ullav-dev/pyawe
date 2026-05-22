# Exceptions

All exceptions inherit from `AweError`, so you can catch everything with a single `except AweError` or target specific cases precisely.

```
AweError (base)
├── AweAuthError       — 401 / 403, or login() not called
├── AweNotFoundError   — 404
├── AweValidationError — 400
└── AweServerError     — 5xx
```

::: pyawe.exceptions.AweError

::: pyawe.exceptions.AweAuthError

::: pyawe.exceptions.AweNotFoundError

::: pyawe.exceptions.AweValidationError

::: pyawe.exceptions.AweServerError
