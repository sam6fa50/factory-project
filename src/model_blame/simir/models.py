from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SimIRModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class BackendMode(str, Enum):
    LIVE = "live"
    REPLAY = "replay"
    MOCK = "mock"


class TelemetryKind(str, Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    STATE = "state"
    COUNTER = "counter"
    METRIC = "metric"
    EVENT = "event"
    ALARM = "alarm"


class Quality(str, Enum):
    GOOD = "good"
    STALE = "stale"
    MISSING = "missing"
    UNCERTAIN = "uncertain"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CommandStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class SimulationBackend(SimIRModel):
    backend_id: str
    name: str
    mode: BackendMode
    protocol: str | None = None
    version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationRun(SimIRModel):
    run_id: str = Field(default_factory=lambda: f"run_{uuid4().hex[:12]}")
    backend: str
    scenario: str | None = None
    mode: BackendMode = BackendMode.MOCK
    started_at: datetime = Field(default_factory=utc_now)
    stopped_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Asset(SimIRModel):
    asset_id: str
    name: str
    kind: str
    parent_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Tag(SimIRModel):
    tag_id: str
    raw_name: str
    asset_id: str
    kind: TelemetryKind
    value_type: Literal["bool", "int", "float", "str", "json"] = "json"
    unit: str | None = None
    writable: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def local_name(self) -> str:
        prefix = f"{self.asset_id}."
        if self.tag_id.startswith(prefix):
            return self.tag_id[len(prefix) :]
        return self.tag_id


class TelemetrySample(SimIRModel):
    timestamp: datetime = Field(default_factory=utc_now)
    sim_time: float | None = None
    run_id: str
    backend: str
    asset_id: str
    tag: str
    kind: TelemetryKind
    value: Any
    quality: Quality = Quality.GOOD
    unit: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> Any:
        if isinstance(value, str) and value.endswith("Z"):
            return value[:-1] + "+00:00"
        return value

    @property
    def full_tag(self) -> str:
        return f"{self.asset_id}.{self.tag}"


class TelemetryBatch(SimIRModel):
    timestamp: datetime = Field(default_factory=utc_now)
    run_id: str
    backend: str
    samples: list[TelemetrySample] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Event(SimIRModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=utc_now)
    sim_time: float | None = None
    run_id: str
    backend: str
    asset_id: str | None = None
    event_type: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Alarm(SimIRModel):
    alarm_id: str = Field(default_factory=lambda: f"alm_{uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=utc_now)
    sim_time: float | None = None
    run_id: str
    backend: str
    asset_id: str | None = None
    severity: Severity
    alarm_type: str
    message: str
    active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class Command(SimIRModel):
    command_id: str = Field(default_factory=lambda: f"cmd_{uuid4().hex[:12]}")
    issued_at: datetime = Field(default_factory=utc_now)
    run_id: str | None = None
    backend: str
    tag_id: str
    value: Any
    status: CommandStatus = CommandStatus.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)


class FaultInjection(SimIRModel):
    fault_id: str = Field(default_factory=lambda: f"flt_{uuid4().hex[:12]}")
    fault_type: str
    asset_id: str | None = None
    tag_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperationResult(SimIRModel):
    ok: bool
    operation: str
    message: str
    value: Any = None
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BackendCapabilities(SimIRModel):
    backend: str
    name: str
    mode: BackendMode
    protocol: str | None = None
    supports_live_stream: bool = False
    supports_polling: bool = True
    supports_write_tags: bool = False
    supports_reset: bool = False
    supports_fault_injection: bool = False
    supported_protocols: list[str] = Field(default_factory=list)
    writable_tags: list[str] = Field(default_factory=list)
    read_only_tags: list[str] = Field(default_factory=list)
    quirks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Residual(SimIRModel):
    residual_id: str
    run_id: str
    asset_id: str
    type: str
    severity: Severity
    expected: dict[str, Any] = Field(default_factory=dict)
    observed: dict[str, Any] = Field(default_factory=dict)
    time_window: dict[str, Any] = Field(default_factory=dict)
    candidate_causes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BlameHypothesis(SimIRModel):
    hypothesis_id: str
    residual_id: str
    primary_blame: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    supporting_evidence: list[str] = Field(default_factory=list)
    next_diagnostic_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
