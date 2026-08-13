from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from model_blame.adapters.factory_io.modbus_client import FactoryIOModbusClient
from model_blame.adapters.factory_io.opcua_client import FactoryIOOpcUaClient
from model_blame.adapters.factory_io.tag_mapper import TagMapper
from model_blame.adapters.factory_io.web_api_client import FactoryIOWebApiClient
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


class FactoryIOConfig(BaseModel):
    backend: str = "factory_io"
    mode: Literal["live", "replay"] = "live"
    protocol: Literal["web_api", "opcua", "modbus", "replay"] = "web_api"
    host: str = "127.0.0.1"
    port: int = 7410
    scene: str = "demo_conveyor"
    polling_interval: float = 0.5
    tag_map_path: str
    endpoints: dict[str, str | None] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "FactoryIOConfig":
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError("PyYAML is required to load SimIR YAML configuration.") from exc
        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return cls.model_validate(data)


class FactoryIOBackendSpecificClient(BackendSpecificClient):
    def __init__(self, adapter: "FactoryIOAdapter"):
        super().__init__(backend=adapter.backend_id, raw_client=adapter.client)
        self.adapter = adapter

    def call(self, operation: str, payload: dict[str, Any] | None = None) -> OperationResult:
        payload = payload or {}
        if operation == "raw_transport_health":
            value = self.adapter.client.health() if hasattr(self.adapter.client, "health") else {}
            return ok("backend_specific.raw_transport_health", value=value)
        if operation == "raw_tag_names":
            return ok("backend_specific.raw_tag_names", value=self.adapter.mapper.raw_names)
        return super().call(operation, payload)


class FactoryIOAdapter(SimulatorAdapter):
    backend_id = "factory_io"

    def __init__(self, config: FactoryIOConfig):
        self.config = config
        self.mapper = TagMapper.from_file(config.tag_map_path)
        self.client: Any = None
        self.run: SimulationRun | None = None
        self.connected = False

    def connect(self) -> OperationResult:
        try:
            self.client = self._make_client()
            self.client.connect()
        except NotImplementedError as exc:
            return failed("connect", str(exc))
        except Exception as exc:  # pragma: no cover - exercised only with live services
            return failed("connect", f"Factory I/O connection failed: {exc}")
        self.connected = True
        return ok("connect", f"Connected to Factory I/O via {self.config.protocol}.")

    def disconnect(self) -> OperationResult:
        if self.client is not None:
            self.client.disconnect()
        self.connected = False
        return ok("disconnect", "Disconnected from Factory I/O.")

    def health(self) -> OperationResult:
        value = {"connected": self.connected, "protocol": self.config.protocol, "scene": self.config.scene}
        if self.client is not None and hasattr(self.client, "health"):
            value["transport"] = self.client.health()
        return ok("health", "Factory I/O adapter health.", value=value)

    def capabilities(self) -> BackendCapabilities:
        tags = self.list_tags()
        return BackendCapabilities(
            backend=self.backend_id,
            name="Factory I/O",
            mode=BackendMode.LIVE if self.config.mode == "live" else BackendMode.REPLAY,
            protocol=self.config.protocol,
            supports_live_stream=False,
            supports_polling=True,
            supports_write_tags=any(tag.writable for tag in tags),
            supports_reset=self.config.protocol == "web_api",
            supports_fault_injection=False,
            supported_protocols=["web_api", "opcua", "modbus", "replay"],
            writable_tags=[tag.tag_id for tag in tags if tag.writable],
            read_only_tags=[tag.tag_id for tag in tags if not tag.writable],
            quirks=[
                "Factory I/O tag names and writable status depend on the selected driver and scene.",
                "Live transport endpoints are configured outside SimIR so the agent can remain backend neutral.",
            ],
        )

    def list_assets(self) -> list[Asset]:
        return self.mapper.assets()

    def list_tags(self) -> list[Tag]:
        return self.mapper.tags()

    def start_run(self, scenario: str | None = None) -> SimulationRun:
        self.run = SimulationRun(
            backend=self.backend_id,
            scenario=scenario or self.config.scene,
            mode=BackendMode.LIVE if self.config.mode == "live" else BackendMode.REPLAY,
            metadata={"protocol": self.config.protocol},
        )
        return self.run

    def stop_run(self) -> OperationResult:
        if self.run is not None:
            self.run.stopped_at = datetime.now().astimezone()
        return ok("stop_run", "Factory I/O run stopped.", value=self.run.model_dump(mode="json") if self.run else None)

    def poll(self) -> TelemetryBatch:
        if self.run is None:
            self.start_run()
        if self.client is None:
            raise RuntimeError("Factory I/O adapter is not connected.")
        raw_values = self.client.read_tags(self.mapper.raw_names)
        return self.mapper.batch_from_raw(
            raw_values=raw_values,
            run_id=self.run.run_id,
            backend=self.backend_id,
            sim_time=None,
        )

    def read_tags(self, tag_ids) -> TelemetryBatch | OperationResult:
        if self.run is None:
            self.start_run()
        raw_names = [self.mapper.raw_for_tag_id(tag_id) for tag_id in tag_ids]
        try:
            raw_values = self.client.read_tags(raw_names)
        except Exception as exc:  # pragma: no cover - live path only
            return failed("read_tags", str(exc), value={"tag_ids": list(tag_ids)})
        return self.mapper.batch_from_raw(raw_values, self.run.run_id, self.backend_id, None, include_all=False)

    def write_tag(self, tag_id: str, value: Any) -> OperationResult:
        tag = next((item for item in self.list_tags() if item.tag_id == tag_id), None)
        if tag is None:
            return failed("write_tag", f"Unknown tag '{tag_id}'.")
        if not tag.writable:
            return unsupported("write_tag", f"Tag '{tag_id}' is read-only.", value={"tag_id": tag_id})
        try:
            self.client.write_tag(self.mapper.raw_for_tag_id(tag_id), value)
        except Exception as exc:  # pragma: no cover - live path only
            return failed("write_tag", str(exc), value={"tag_id": tag_id, "value": value})
        return ok("write_tag", "Tag write accepted.", value={"tag_id": tag_id, "value": value})

    def reset(self) -> OperationResult:
        if self.client is None or not hasattr(self.client, "reset"):
            return unsupported("reset")
        try:
            self.client.reset()
        except Exception as exc:  # pragma: no cover - live path only
            return failed("reset", str(exc))
        return ok("reset", "Factory I/O reset command accepted.")

    def inject_fault(self, fault_spec: FaultInjection) -> OperationResult:
        return unsupported("inject_fault", value=fault_spec.model_dump(mode="json"))

    def backend_specific(self) -> BackendSpecificClient:
        return FactoryIOBackendSpecificClient(self)

    def _make_client(self):
        if self.config.protocol == "web_api":
            return FactoryIOWebApiClient(self.config.host, self.config.port, endpoints=self.config.endpoints)
        if self.config.protocol == "opcua":
            return FactoryIOOpcUaClient(self.config.host, self.config.port)
        if self.config.protocol == "modbus":
            return FactoryIOModbusClient(self.config.host, self.config.port)
        raise NotImplementedError("Replay transport is handled by the mock adapter in this MVP.")
