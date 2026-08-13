from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from model_blame.adapters.factory_io.tag_mapper import TagMapper
from model_blame.simir.adapter import BackendSpecificClient, SimulatorAdapter
from model_blame.simir.capabilities import failed, ok, unsupported
from model_blame.simir.models import (
    Asset,
    BackendCapabilities,
    BackendMode,
    FaultInjection,
    OperationResult,
    SimulationRun,
    Tag,
    TelemetryBatch,
)


class MockFactoryIOConfig(BaseModel):
    backend: str = "factory_io"
    mode: Literal["mock"] = "mock"
    scene: str = "demo_conveyor"
    scenario: Literal["normal", "missing_exit", "delayed_transition"] = "normal"
    polling_interval: float = 0.5
    tag_map_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path, **overrides: Any) -> "MockFactoryIOConfig":
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError("PyYAML is required to load SimIR YAML configuration.") from exc
        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        data.update(overrides)
        return cls.model_validate(data)


class MockBackendSpecificClient(BackendSpecificClient):
    def __init__(self, adapter: "MockFactoryIOAdapter"):
        super().__init__(backend=adapter.backend_id, raw_client=adapter)
        self.adapter = adapter

    def call(self, operation: str, payload: dict[str, Any] | None = None) -> OperationResult:
        if operation == "scenario_state":
            return ok(
                "backend_specific.scenario_state",
                value={
                    "scenario": self.adapter.config.scenario,
                    "sim_time": self.adapter.sim_time,
                    "overrides": self.adapter.overrides,
                },
            )
        return super().call(operation, payload)


class MockFactoryIOAdapter(SimulatorAdapter):
    """Synthetic Factory I/O-style source used when no simulator is running."""

    backend_id = "factory_io"

    def __init__(self, config: MockFactoryIOConfig):
        self.config = config
        self.mapper = TagMapper.from_file(config.tag_map_path)
        self.run: SimulationRun | None = None
        self.connected = False
        self.sim_time = 0.0
        self.overrides: dict[str, Any] = {}

    def connect(self) -> OperationResult:
        self.connected = True
        return ok("connect", "Mock Factory I/O adapter connected.")

    def disconnect(self) -> OperationResult:
        self.connected = False
        return ok("disconnect", "Mock Factory I/O adapter disconnected.")

    def health(self) -> OperationResult:
        return ok(
            "health",
            "Mock Factory I/O adapter health.",
            value={"connected": self.connected, "scenario": self.config.scenario, "sim_time": self.sim_time},
        )

    def capabilities(self) -> BackendCapabilities:
        tags = self.list_tags()
        return BackendCapabilities(
            backend=self.backend_id,
            name="Mock Factory I/O",
            mode=BackendMode.MOCK,
            protocol="synthetic",
            supports_live_stream=False,
            supports_polling=True,
            supports_write_tags=True,
            supports_reset=True,
            supports_fault_injection=False,
            supported_protocols=["mock"],
            writable_tags=[tag.tag_id for tag in tags if tag.writable],
            read_only_tags=[tag.tag_id for tag in tags if not tag.writable],
            quirks=["Synthetic telemetry advances only when poll() is called."],
        )

    def list_assets(self) -> list[Asset]:
        return self.mapper.assets()

    def list_tags(self) -> list[Tag]:
        return self.mapper.tags()

    def start_run(self, scenario: str | None = None) -> SimulationRun:
        if scenario is not None:
            self.config.scenario = scenario  # type: ignore[assignment]
        self.sim_time = 0.0
        self.overrides = {}
        self.run = SimulationRun(
            backend=self.backend_id,
            scenario=self.config.scenario,
            mode=BackendMode.MOCK,
            metadata={"scene": self.config.scene},
        )
        return self.run

    def stop_run(self) -> OperationResult:
        if self.run is not None:
            self.run.stopped_at = datetime.now().astimezone()
        return ok("stop_run", "Mock run stopped.", value=self.run.model_dump(mode="json") if self.run else None)

    def reset(self) -> OperationResult:
        self.sim_time = 0.0
        self.overrides = {}
        return ok("reset", "Mock simulation reset.")

    def poll(self) -> TelemetryBatch:
        if self.run is None:
            self.start_run()
        raw_values = self._raw_values_at(self.sim_time)
        batch = self.mapper.batch_from_raw(raw_values, self.run.run_id, self.backend_id, self.sim_time)
        self.sim_time = round(self.sim_time + self.config.polling_interval, 6)
        return batch

    def read_tags(self, tag_ids) -> TelemetryBatch | OperationResult:
        if self.run is None:
            self.start_run()
        raw_values = self._raw_values_at(self.sim_time)
        selected_raw_names = [self.mapper.raw_for_tag_id(tag_id) for tag_id in tag_ids]
        selected_values = {raw_name: raw_values[raw_name] for raw_name in selected_raw_names}
        return self.mapper.batch_from_raw(selected_values, self.run.run_id, self.backend_id, self.sim_time, include_all=False)

    def write_tag(self, tag_id: str, value: Any) -> OperationResult:
        tag = next((item for item in self.list_tags() if item.tag_id == tag_id), None)
        if tag is None:
            return failed("write_tag", f"Unknown tag '{tag_id}'.")
        if not tag.writable:
            return unsupported("write_tag", f"Tag '{tag_id}' is read-only.", value={"tag_id": tag_id})
        raw_name = self.mapper.raw_for_tag_id(tag_id)
        self.overrides[raw_name] = value
        return ok("write_tag", "Mock tag override accepted.", value={"tag_id": tag_id, "value": value})

    def inject_fault(self, fault_spec: FaultInjection) -> OperationResult:
        return unsupported("inject_fault", value=fault_spec.model_dump(mode="json"))

    def backend_specific(self) -> BackendSpecificClient:
        return MockBackendSpecificClient(self)

    def _raw_values_at(self, sim_time: float) -> dict[str, Any]:
        scenario = self.config.scenario
        motor = bool(self.overrides.get("ConveyorMotor", True))
        entry = 1.0 <= sim_time < 1.5
        blocked = False
        exit_sensor = False
        part_counter = 0

        if scenario == "normal":
            exit_sensor = 3.0 <= sim_time < 3.5
            part_counter = 1 if sim_time >= 3.0 else 0
        elif scenario == "missing_exit":
            blocked = sim_time >= 4.5
            exit_sensor = False
            part_counter = 0
        elif scenario == "delayed_transition":
            exit_sensor = 5.5 <= sim_time < 6.0
            part_counter = 1 if sim_time >= 5.5 else 0

        speed = 0.65 if motor and not blocked else 0.0
        raw = {
            "SensorEntry": entry,
            "SensorExit": exit_sensor,
            "ConveyorMotor": motor,
            "ConveyorSpeed": speed,
            "PartCounter": part_counter,
            "BlockedSensor": blocked,
            "MachineRunning": motor,
        }
        raw.update(self.overrides)
        return raw
