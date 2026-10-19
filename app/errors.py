from __future__ import annotations


class ApiError(Exception):
    """Erreur métier sérialisée par le handler global de app.main."""

    status_code = 400
    code = "bad_request"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class NotFoundError(ApiError):
    status_code = 404
    code = "not_found"


class ConflictError(ApiError):
    status_code = 409
    code = "conflict"


class UnprocessableError(ApiError):
    status_code = 422
    code = "unprocessable"
