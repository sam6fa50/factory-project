from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable
from typing import Any

from .capabilities import unsupported
from .models import (
    Asset,
    BackendCapabilities,
    FaultInjection,
    OperationResult,
    SimulationRun,
    TelemetryBatch,
    TelemetrySample,
)


class BackendSpecificClient:
    """Controlled escape hatch for simulator-specific operations."""

    def __init__(self, backend: str, raw_client: Any = None):
        self.backend = backend
        self.raw_client = raw_client

    def call(self, operation: str, payload: dict[str, Any] | None = None) -> OperationResult:
        return unsupported(
            operation=f"backend_specific.{operation}",
            message=f"{self.backend} does not expose backend-specific operation '{operation}'.",
            value={"payload": payload or {}},
        )


class SimulatorAdapter(ABC):
    """Base interface for all simulation telemetry adapters."""

    backend_id: str

    @abstractmethod
    def connect(self) -> OperationResult:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> OperationResult:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> OperationResult:
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        raise NotImplementedError

    @abstractmethod
    def list_assets(self) -> list[Asset]:
        raise NotImplementedError

    @abstractmethod
    def list_tags(self):
        raise NotImplementedError

    @abstractmethod
    def poll(self) -> TelemetryBatch:
        raise NotImplementedError

    @abstractmethod
    def start_run(self, scenario: str | None = None) -> SimulationRun:
        raise NotImplementedError

    @abstractmethod
    def stop_run(self) -> OperationResult:
        raise NotImplementedError

    def read_tag(self, tag_id: str) -> TelemetrySample | OperationResult:
        result = self.read_tags([tag_id])
        if isinstance(result, OperationResult):
            return result
        return result.samples[0] if result.samples else unsupported("read_tag", "No sample returned.")

    def read_tags(self, tag_ids: Iterable[str]) -> TelemetryBatch | OperationResult:
        return unsupported("read_tags", value={"tag_ids": list(tag_ids)})

    def stream(self) -> Generator[TelemetryBatch, None, None]:
        while True:
            yield self.poll()

    def write_tag(self, tag_id: str, value: Any) -> OperationResult:
        return unsupported("write_tag", value={"tag_id": tag_id, "value": value})

    def reset(self) -> OperationResult:
        return unsupported("reset")

    def inject_fault(self, fault_spec: FaultInjection) -> OperationResult:
        return unsupported("inject_fault", value=fault_spec.model_dump(mode="json"))

    def clear_fault(self, fault_id: str) -> OperationResult:
        return unsupported("clear_fault", value={"fault_id": fault_id})

    def backend_specific(self) -> BackendSpecificClient:
        return BackendSpecificClient(backend=self.backend_id)
