from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(message=message, error_code=error_code, status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", error_code: str = "VALIDATION_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=400)


class ProviderUnavailableError(AppError):
    def __init__(
        self,
        message: str = "Provider unavailable",
        error_code: str = "PROVIDER_UNAVAILABLE",
    ):
        super().__init__(message=message, error_code=error_code, status_code=502)


class InternalError(AppError):
    def __init__(self, message: str = "Internal server error", error_code: str = "INTERNAL_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=500)


async def app_error_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    error_code = getattr(exc, "error_code", "INTERNAL_ERROR")
    message = getattr(exc, "message", str(exc))
    status_code = getattr(exc, "status_code", 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": error_code,
            "message": message,
            "request_id": request_id,
        },
    )
