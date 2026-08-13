from __future__ import annotations

from datetime import datetime
from typing import Any

from model_blame.blame.hypotheses import BlameHypothesisGenerator
from model_blame.blame.report import build_blame_report
from model_blame.residuals.engine import ResidualEngine
from model_blame.simir.adapter import SimulatorAdapter
from model_blame.simir.models import FaultInjection, OperationResult, Residual, TelemetrySample
from model_blame.telemetry.pooler import TelemetryPooler


class SimClient:
    """Agent-facing API over SimIR, not over Factory I/O internals."""

    def __init__(
        self,
        adapter: SimulatorAdapter,
        residual_engine: ResidualEngine,
        hypothesis_generator: BlameHypothesisGenerator | None = None,
        pooler: TelemetryPooler | None = None,
    ):
        self.adapter = adapter
        self.residual_engine = residual_engine
        self.hypothesis_generator = hypothesis_generator or BlameHypothesisGenerator()
        self.pooler = pooler or TelemetryPooler(adapter)
        self._residuals: list[Residual] = []

    def start(self, scenario: str | None = None) -> None:
        self.pooler.connect()
        self.pooler.start_run(scenario=scenario)

    def poll_once(self):
        return self.pooler.poll_once()

    def poll_for(self, duration_seconds: float, sleep: bool = False):
        return self.pooler.poll_for(duration_seconds, sleep=sleep)

    def status(self) -> dict[str, Any]:
        return {
            "backend": self.current_backend(),
            "health": self.adapter.health().model_dump(mode="json"),
            "run": self.pooler.run.model_dump(mode="json") if self.pooler.run else None,
            "samples_buffered": len(self.pooler.buffer.samples),
        }

    def capabilities(self):
        return self.adapter.capabilities()

    def current_backend(self) -> str:
        return self.adapter.backend_id

    def list_assets(self):
        return self.adapter.list_assets()

    def list_tags(self):
        return self.adapter.list_tags()

    def recent_samples(
        self,
        asset_id: str | None = None,
        tag: str | None = None,
        since: datetime | float | None = None,
        limit: int | None = None,
    ) -> list[TelemetrySample]:
        return self.pooler.buffer.recent(asset_id=asset_id, tag=tag, since=since, limit=limit)

    def recent_residuals(self) -> list[Residual]:
        self._residuals = self.residual_engine.evaluate(self.pooler.buffer.recent())
        return self._residuals

    def blame_report(self) -> str:
        residuals = self.recent_residuals()
        hypotheses = self.hypothesis_generator.generate(residuals, self.recent_samples(), self.pooler.features())
        return build_blame_report(self.pooler.run, residuals, hypotheses, self.pooler.features())

    def write_tag(self, tag_id: str, value: Any) -> OperationResult:
        return self.adapter.write_tag(tag_id, value)

    def inject_fault(self, fault_spec: FaultInjection) -> OperationResult:
        return self.adapter.inject_fault(fault_spec)

    def backend_specific(self, operation: str, payload: dict[str, Any] | None = None) -> OperationResult:
        return self.adapter.backend_specific().call(operation, payload)
