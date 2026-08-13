from __future__ import annotations

import time
from pathlib import Path

from model_blame.simir.adapter import SimulatorAdapter
from model_blame.simir.models import OperationResult, SimulationRun, TelemetryBatch
from model_blame.telemetry.buffer import TelemetryBuffer
from model_blame.telemetry.features import DerivedFeatures, FeatureState
from model_blame.telemetry.logger import TelemetryLogger


class TelemetryPooler:
    def __init__(
        self,
        adapter: SimulatorAdapter,
        buffer: TelemetryBuffer | None = None,
        logger: TelemetryLogger | None = None,
        jsonl_log_path: str | Path | None = None,
        sqlite_log_path: str | Path | None = None,
    ):
        self.adapter = adapter
        self.buffer = buffer or TelemetryBuffer()
        self.logger = logger or TelemetryLogger(jsonl_log_path, sqlite_log_path)
        self.feature_state = FeatureState(expected_tags=[tag.tag_id for tag in adapter.list_tags()])
        self.run: SimulationRun | None = None

    def connect(self) -> OperationResult:
        return self.adapter.connect()

    def start_run(self, scenario: str | None = None) -> SimulationRun:
        self.run = self.adapter.start_run(scenario=scenario)
        return self.run

    def stop_run(self) -> OperationResult:
        return self.adapter.stop_run()

    def poll_once(self) -> TelemetryBatch:
        batch = self.adapter.poll()
        self.buffer.append_batch(batch)
        self.logger.log_batch(batch)
        self.feature_state.update(batch.samples)
        return batch

    def poll_for(self, duration_seconds: float, sleep: bool = False) -> list[TelemetryBatch]:
        capabilities = self.adapter.capabilities()
        interval = float(capabilities.metadata.get("polling_interval", 0.5)) if capabilities.metadata else 0.5
        if hasattr(self.adapter, "config") and hasattr(self.adapter.config, "polling_interval"):
            interval = float(self.adapter.config.polling_interval)
        count = max(1, int(duration_seconds / interval) + 1)
        batches = []
        for _ in range(count):
            batches.append(self.poll_once())
            if sleep:
                time.sleep(interval)
        return batches

    def features(self) -> DerivedFeatures:
        last_sim_time = None
        if self.buffer.samples:
            last_sample = self.buffer.samples[-1]
            last_sim_time = last_sample.sim_time
        return self.feature_state.snapshot(last_sim_time)
