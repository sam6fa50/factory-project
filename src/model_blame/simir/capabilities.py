from __future__ import annotations

from typing import Any

from .models import OperationResult


def unsupported(operation: str, message: str | None = None, value: Any = None) -> OperationResult:
    return OperationResult(
        ok=False,
        operation=operation,
        message=message or f"{operation} is not supported by this backend.",
        value=value,
        error_code="unsupported",
    )


def failed(operation: str, message: str, value: Any = None) -> OperationResult:
    return OperationResult(
        ok=False,
        operation=operation,
        message=message,
        value=value,
        error_code="failed",
    )


def ok(operation: str, message: str = "ok", value: Any = None) -> OperationResult:
    return OperationResult(ok=True, operation=operation, message=message, value=value)
