from __future__ import annotations

from collections import deque
from datetime import datetime

from model_blame.simir.models import TelemetryBatch, TelemetrySample


class TelemetryBuffer:
    def __init__(self, max_samples: int = 10000):
        self.samples: deque[TelemetrySample] = deque(maxlen=max_samples)

    def append(self, sample: TelemetrySample) -> None:
        self.samples.append(sample)

    def append_batch(self, batch: TelemetryBatch) -> None:
        self.samples.extend(batch.samples)

    def recent(
        self,
        asset_id: str | None = None,
        tag: str | None = None,
        since: datetime | float | None = None,
        limit: int | None = None,
    ) -> list[TelemetrySample]:
        values = list(self.samples)
        if asset_id is not None:
            values = [sample for sample in values if sample.asset_id == asset_id]
        if tag is not None:
            values = [sample for sample in values if sample.tag == tag or sample.full_tag == tag]
        if since is not None:
            if isinstance(since, datetime):
                values = [sample for sample in values if sample.timestamp >= since]
            else:
                values = [sample for sample in values if sample.sim_time is not None and sample.sim_time >= since]
        if limit is not None:
            values = values[-limit:]
        return values

    def last_by_tag(self) -> dict[str, TelemetrySample]:
        latest: dict[str, TelemetrySample] = {}
        for sample in self.samples:
            latest[sample.full_tag] = sample
        return latest

    def clear(self) -> None:
        self.samples.clear()
