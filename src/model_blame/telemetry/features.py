from __future__ import annotations

from pydantic import BaseModel, Field

from model_blame.simir.models import TelemetrySample


class DerivedFeatures(BaseModel):
    last_values: dict[str, object] = Field(default_factory=dict)
    value_changes: list[dict[str, object]] = Field(default_factory=list)
    missing_tags: list[str] = Field(default_factory=list)
    stale_tags: list[str] = Field(default_factory=list)
    transition_durations: list[dict[str, object]] = Field(default_factory=list)
    cycle_times: list[dict[str, object]] = Field(default_factory=list)
    throughput_count: int = 0
    blocked_assets: list[str] = Field(default_factory=list)
    starved_assets: list[str] = Field(default_factory=list)


class FeatureState:
    def __init__(self, expected_tags: list[str] | None = None, stale_after_seconds: float = 2.0):
        self.expected_tags = expected_tags or []
        self.stale_after_seconds = stale_after_seconds
        self.last_values: dict[str, object] = {}
        self.last_seen_sim_time: dict[str, float] = {}
        self.value_changes: list[dict[str, object]] = []
        self.transition_durations: list[dict[str, object]] = []
        self.cycle_times: list[dict[str, object]] = []
        self._last_transition_time: dict[str, float] = {}
        self._pending_entry_time: dict[str, float] = {}
        self.throughput_count = 0
        self.blocked_assets: set[str] = set()

    def update(self, samples: list[TelemetrySample]) -> DerivedFeatures:
        for sample in sorted(samples, key=lambda item: (item.sim_time is None, item.sim_time or 0.0, item.full_tag)):
            full_tag = sample.full_tag
            sim_time = sample.sim_time
            previous = self.last_values.get(full_tag)
            if sim_time is not None:
                self.last_seen_sim_time[full_tag] = sim_time

            if full_tag not in self.last_values or previous != sample.value:
                change = {
                    "tag": full_tag,
                    "from": previous,
                    "to": sample.value,
                    "sim_time": sim_time,
                }
                self.value_changes.append(change)
                if sim_time is not None and full_tag in self._last_transition_time:
                    self.transition_durations.append(
                        {
                            "tag": full_tag,
                            "duration": sim_time - self._last_transition_time[full_tag],
                            "ended_at": sim_time,
                        }
                    )
                if sim_time is not None:
                    self._last_transition_time[full_tag] = sim_time

            self.last_values[full_tag] = sample.value

            if sample.kind == "counter" and isinstance(sample.value, int):
                self.throughput_count = max(self.throughput_count, sample.value)
            if sample.tag == "blocked_sensor" and sample.value:
                self.blocked_assets.add(sample.asset_id)

            self._track_cycle_time(sample)

        return self.snapshot()

    def snapshot(self, current_sim_time: float | None = None) -> DerivedFeatures:
        missing = [tag for tag in self.expected_tags if tag not in self.last_values]
        stale: list[str] = []
        if current_sim_time is not None:
            for tag in self.expected_tags:
                last_seen = self.last_seen_sim_time.get(tag)
                if last_seen is None:
                    continue
                if current_sim_time - last_seen > self.stale_after_seconds:
                    stale.append(tag)
        return DerivedFeatures(
            last_values=dict(self.last_values),
            value_changes=list(self.value_changes),
            missing_tags=missing,
            stale_tags=stale,
            transition_durations=list(self.transition_durations),
            cycle_times=list(self.cycle_times),
            throughput_count=self.throughput_count,
            blocked_assets=sorted(self.blocked_assets),
            starved_assets=[],
        )

    def _track_cycle_time(self, sample: TelemetrySample) -> None:
        if sample.sim_time is None or not bool(sample.value):
            return
        if sample.tag == "entry_sensor":
            self._pending_entry_time[sample.asset_id] = sample.sim_time
        elif sample.tag == "exit_sensor" and sample.asset_id in self._pending_entry_time:
            start = self._pending_entry_time.pop(sample.asset_id)
            self.cycle_times.append(
                {
                    "asset_id": sample.asset_id,
                    "entry_tag": f"{sample.asset_id}.entry_sensor",
                    "exit_tag": f"{sample.asset_id}.exit_sensor",
                    "cycle_time": sample.sim_time - start,
                    "started_at": start,
                    "ended_at": sample.sim_time,
                }
            )
